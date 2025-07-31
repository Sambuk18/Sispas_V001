from sqlalchemy import text
from datetime import datetime, date
from threading import Lock
import logging
from typing import List, Dict, Any, Tuple
import json
import hashlib
import dbfread
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from app import db

# Configuración de logging
logger = logging.getLogger(__name__)

# Bloqueo para operaciones thread-safe
sync_lock = Lock()

# Estado de sincronización (debería definirse en otro módulo o aquí)
sync_status = {
    'last_check': None,
    'last_positions': {},
    'total_processed': 0,
    'errors': [],
    'active': True
}

def calculate_hash(record: Dict[str, Any]) -> str:
    """Calcula hash MD5 de un registro"""
    def json_serializer(obj):
        """Serializador personalizado para tipos no estándar"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
    
    record_str = json.dumps(record, sort_keys=True, default=json_serializer).encode('utf-8')
    return hashlib.md5(record_str).hexdigest()

def read_dbf(file_name: str) -> List[Dict[str, Any]]:
    """Lee un archivo DBF"""
    try:
        table = dbfread.DBF(file_name, encoding='latin1')
        return [dict(record) for record in table]
    except Exception as e:
        logger.error(f"Error leyendo DBF {file_name}: {str(e)}")
        return []

def get_new_records(file_name: str, last_positions: Dict[str, int]) -> Tuple[List[Dict[str, Any]], int]:
    """Obtiene nuevos registros desde última posición"""
    records = read_dbf(file_name)
    last_pos = last_positions.get(file_name, 0)
    
    # Para SCLIENTE, siempre leer todos los registros ya que pueden haber modificaciones
    if file_name.lower().endswith('scliente.dbf'):
        return records, len(records)
    
    new_records = records[last_pos:]
    return new_records, len(records)

def get_dbf_structure(file_name: str) -> Dict[str, str]:
    """Obtiene estructura de un archivo DBF"""
    try:
        table = dbfread.DBF(file_name, encoding='latin1')
        return {field.name: field.type for field in table.fields}
    except Exception as e:
        logger.error(f"Error obteniendo estructura DBF {file_name}: {str(e)}")
        return {}

def find_dbf_file(base_name: str) -> Path:
    """Encuentra archivos DBF insensible a mayúsculas"""
    base_path = Path(Config.DBF_DIRECTORY)
    for file in base_path.glob('*'):
        if file.suffix.lower() == '.dbf' and file.stem.lower() == base_name.lower():
            return file
    return None

def _table_exists(conn, table_name: str) -> bool:
    """Verifica si una tabla existe"""
    result = conn.execute(text("SHOW TABLES LIKE :table"), {'table': table_name})
    return result.fetchone() is not None

def _get_table_structure(conn, table_name: str) -> Dict[str, str]:
    """Obtiene estructura de la tabla"""
    result = conn.execute(text(f"DESCRIBE `{table_name}`"))
    return {row[0].lower(): row[1] for row in result}


def _convert_value(value: Any, column_type: str) -> Any:
    """Convierte valores a tipos adecuados para SQL"""
    if value is None:
        return None
    if 'int' in column_type.lower():
        return int(value) if str(value).isdigit() else None
    if 'decimal' in column_type.lower() or 'float' in column_type.lower() or 'double' in column_type.lower():
        try:
            return float(value)
        except ValueError:
            return None
    if 'date' in column_type.lower() or 'datetime' in column_type.lower():
        try:
            if isinstance(value, (date, datetime)):
                return value
            return datetime.strptime(str(value), '%Y-%m-%d') if value else None
        except ValueError:
            return None
    return str(value)

def _prepare_sql_queries(table_name: str, fields: List[str]) -> Dict[str, str]:
    """Prepara consultas SQL para insert/update con manejo especial para SCLIENTE"""
    field_keys = [f.lower() for f in fields]
    sql_fields = [f"`{f}`" for f in field_keys]

    # Asegurarse que el nombre de la tabla está correctamente escapado
    safe_table_name = f"`{table_name}`"

    insert = f"""
        INSERT INTO {safe_table_name} ({', '.join(sql_fields + ['`control_hash`'])})
        VALUES ({', '.join([f':{f}' for f in field_keys] + [':control_hash'])})
    """

    # Consultas específicas para SCLIENTE
    if table_name.lower() == 'scliente':
        update = f"""
            UPDATE {safe_table_name}
            SET {', '.join([f'`{f}` = :{f}' for f in field_keys if f != 'nro_cli'] + ['`control_hash` = :control_hash'])}
            WHERE `nro_cli` = :nro_cli
        """
        check = f"SELECT `control_hash` FROM {safe_table_name} WHERE `nro_cli` = :nro_cli LIMIT 1"
    else:
        # Consultas estándar para otras tablas
        update = f"""
            UPDATE {safe_table_name}
            SET {', '.join([f'`{f}` = :{f}' for f in field_keys if f != 'control_hash'] + ['`control_hash` = :control_hash'])}
            WHERE `control_hash` = :control_hash
        """
        check = f"SELECT 1 FROM {safe_table_name} WHERE `control_hash` = :control_hash LIMIT 1"

    return {'insert': insert, 'update': update, 'check': check}

def _process_client_record(conn, table_name: str, record: Dict[str, Any], queries: Dict[str, str], table_structure: Dict[str, str]):
    """Procesamiento especial para registros de clientes usando nro_cli como referencia"""
    try:
        record_hash = calculate_hash(record)
        values = {}
        
        # Mapear todos los campos disponibles
        for field in record.keys():
            field_lower = field.lower()
            if field_lower in table_structure:
                values[field_lower] = _convert_value(record[field], table_structure[field_lower])

        # Verificar si el campo nro_cli existe en la estructura de la tabla
        if 'nro_cli' not in table_structure:
            logger.error("La tabla SCLIENTE no tiene columna 'nro_cli'")
            return 0, 0

        # Obtener el número de cliente (nro_cli) del registro
        nro_cli_key = next((k for k in record.keys() if k.lower() == 'nro_cli'), None)
        nro_cli = values.get('nro_cli') or (record.get(nro_cli_key) if nro_cli_key else None)
        
        if not nro_cli:
            logger.warning(f"Registro de cliente sin nro_cli válido. Campos disponibles: {list(record.keys())}")
            return 0, 0

        # Asegurarse que el nro_cli está en los valores
        values['nro_cli'] = nro_cli
        values['control_hash'] = record_hash

        # Verificar si el cliente ya existe y obtener su hash actual
        existing_hash = conn.execute(
            text(queries['check']),
            {'nro_cli': nro_cli}
        ).scalar()

        if existing_hash:
            if existing_hash == record_hash:
                # No hay cambios, no necesita actualización
                logger.debug(f"Registro sin cambios para nro_cli: {nro_cli}")
                return 0, 0
            else:
                # Actualizar registro existente
                conn.execute(
                    text(queries['update']),
                    {**values, 'nro_cli': nro_cli}
                )
                logger.debug(f"Actualizado cliente nro_cli: {nro_cli}")
                return 0, 1
        else:
            # Insertar nuevo registro
            conn.execute(text(queries['insert']), values)
            logger.debug(f"Insertado nuevo cliente nro_cli: {nro_cli}")
            return 1, 0

    except Exception as e:
        logger.error(f"Error procesando registro de cliente: {str(e)}", exc_info=True)
        return 0, 0


def insert_records(engine, table_name: str, records: List[Dict[str, Any]], batch_size: int = 100):
    """Inserta registros en la base de datos con manejo especial para carga inicial"""
    if not records:
        return 0, 0, []

    inserted, updated = 0, 0
    errors = []

    try:
        with engine.begin() as conn:
            if not _table_exists(conn, table_name):
                logger.error(f"La tabla {table_name} no existe en la base de datos")
                return 0, 0, [f"La tabla {table_name} no existe"]

            table_structure = _get_table_structure(conn, table_name)
            if not table_structure:
                logger.error(f"No se pudo obtener estructura de {table_name}")
                return 0, 0, [f"No se pudo obtener estructura de {table_name}"]

            # Verificar si es la tabla SCLIENTE y está vacía (carga inicial)
            is_initial_load = False
            if table_name.lower() == 'scliente':
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).fetchone()
                is_initial_load = count_result[0] == 0
                logger.debug(f"SCLIENTE - Carga inicial: {is_initial_load}")

            queries = _prepare_sql_queries(table_name, [k for k in records[0].keys()
                                        if k.lower() in table_structure])

            for record in records:
                try:
                    if table_name.lower() == 'scliente':
                        # Procesamiento especial para SCLIENTE
                        i, u = _process_client_record(conn, table_name, record, queries, table_structure)
                        inserted += i
                        updated += u
                    else:
                        # Procesamiento normal para otras tablas
                        record_hash = calculate_hash(record)
                        values = {}
                        for field in record.keys():
                            field_lower = field.lower()
                            if field_lower in table_structure:
                                values[field_lower] = _convert_value(record[field], table_structure[field_lower])

                        values['control_hash'] = record_hash

                        exists = conn.execute(
                            text(queries['check']),
                            {'control_hash': record_hash}
                        ).fetchone()

                        if exists:
                            conn.execute(text(queries['update']), values)
                            updated += 1
                        else:
                            conn.execute(text(queries['insert']), values)
                            inserted += 1

                except Exception as e:
                    error_msg = f"Error procesando registro: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)

        logger.info(f"Procesados: {inserted} insertados, {updated} actualizados en {table_name}")
        return inserted, updated, errors

    except SQLAlchemyError as e:
        error_msg = f"Error de base de datos: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg, exc_info=True)
        return 0, 0, errors

def sync_dbf_to_mariadb():
    """Sincroniza archivos DBF con MariaDB"""
    with sync_lock:
        sync_status['last_check'] = datetime.now()
        processed = 0
        total_inserted = 0
        total_updated = 0

        logger.info(f"Iniciando sincronización. Directorio DBF: {Config.DBF_DIRECTORY}")

        for file_name in Config.DBF_FILES:
            try:
                logger.debug(f"Procesando archivo: {file_name}")
                dbf_file = find_dbf_file(file_name)
                if not dbf_file:
                    msg = f"Archivo {file_name} no encontrado en {Config.DBF_DIRECTORY}"
                    sync_status['errors'].append(msg)
                    logger.error(msg)
                    continue

                logger.info(f"Leyendo archivo: {dbf_file}")
                new_records, total_records = get_new_records(str(dbf_file), sync_status['last_positions'])

                if not new_records:
                    logger.debug(f"No hay nuevos registros en {file_name}")
                    continue

                logger.info(f"Procesando {len(new_records)} registros para {file_name}")
                table_name = file_name.replace('.dbf', '').lower()
                inserted, updated, errors = insert_records(db.engine, table_name, new_records)

                total_inserted += inserted
                total_updated += updated
                processed += len(new_records)

                if errors:
                    sync_status['errors'].extend(errors)

                # Para SCLIENTE, no actualizamos last_positions ya que siempre leemos todo el archivo
                if not file_name.lower().endswith('scliente.dbf'):
                    sync_status['last_positions'][file_name] = total_records

            except Exception as e:
                error_msg = f"Error procesando {file_name}: {str(e)}"
                sync_status['errors'].append(error_msg)
                logger.error(error_msg, exc_info=True)

        sync_status['total_processed'] += processed

        return {
            'total_inserted': total_inserted,
            'total_updated': total_updated,
            'total_processed': processed,
            'errors': sync_status['errors'][-10:]
        }

def start_monitor():
    """Inicia el monitor de sincronización"""
    # Implementación del monitor si es necesario
    pass