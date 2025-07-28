import logging
from datetime import date, datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy import text
from app import db
from .dbf_utils import read_dbf, calculate_hash

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table_from_dbf(engine, file_name: str, force_recreate: bool = False) -> bool:
    table_name = file_name.replace('.dbf', '').lower()

    try:
        with engine.begin() as conn:
            result = conn.execute(text(f"SHOW TABLES LIKE :table"), {'table': table_name})
            if result.fetchone():
                if force_recreate:
                    conn.execute(text(f"DROP TABLE `{table_name}`"))
                else:
                    logger.info(f"Tabla {table_name} ya existe - continuando")
                    return True

            all_records = read_dbf(file_name)
            if not all_records:
                logger.error(f"No se pudieron leer registros de {file_name}")
                return False

            columns = []
            for field in all_records[0].keys():
                col_type = _determine_column_type(field, all_records[0], all_records)
                columns.append(f"`{field.lower()}` {col_type}")

            columns.insert(0, '`id` INT AUTO_INCREMENT PRIMARY KEY')
            columns.append("`control_hash` VARCHAR(32) NOT NULL UNIQUE")
            columns.append("`sync_date` DATETIME DEFAULT CURRENT_TIMESTAMP")
            columns.append("`dbf_source` VARCHAR(255) DEFAULT NULL")

            create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  " + ",\n  ".join(columns) + "\n)"
            conn.execute(text(create_sql))
            logger.info(f"Tabla {table_name} creada exitosamente")
            return True

    except Exception as e:
        logger.error(f"Error creando tabla {table_name}: {str(e)}")
        return False

def insert_records(engine, table_name: str, records: List[Dict[str, Any]], batch_size: int = 100):
    if not records:
        return 0, 0, []

    inserted, updated = 0, 0
    errors = []

    with engine.begin() as conn:
        if not _validate_table_exists(conn, table_name):
            return 0, 0, [f"La tabla {table_name} no existe"]

        structure = _get_table_structure(conn, table_name)
        if not structure:
            return 0, 0, [f"No se pudo obtener estructura de {table_name}"]

        queries = _prepare_sql_queries(table_name, [k for k in records[0].keys() if k.lower() in structure])

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            for record in batch:
                try:
                    values = {}
                    for field in record.keys():
                        field_lower = field.lower()
                        if field_lower in structure:
                            values[field_lower] = _convert_value(record[field], structure[field_lower])

                    record_hash = calculate_hash(record)
                    exists = conn.execute(text(queries['check']), {'hash': record_hash}).fetchone()

                    if exists:
                        values['hash'] = record_hash
                        conn.execute(text(queries['update']), values)
                        updated += 1
                    else:
                        values['control_hash'] = record_hash
                        conn.execute(text(queries['insert']), values)
                        inserted += 1

                except Exception as e:
                    error_msg = f"Error procesando registro: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    errors += 1                   

    return inserted, updated, errors

def _validate_table_exists(conn, table_name: str) -> bool:
    result = conn.execute(text(f"SHOW TABLES LIKE :table"), {'table': table_name})
    return result.fetchone() is not None

def _get_table_structure(conn, table_name: str) -> Dict[str, str]:
    result = conn.execute(text(f"DESCRIBE `{table_name}`"))
    return {row[0].lower(): row[1] for row in result.fetchall()}

def _prepare_sql_queries(table_name: str, fields: List[str]) -> Dict[str, str]:
    field_keys = [f.lower() for f in fields]
    sql_fields = [f"`{f}`" for f in field_keys]

    insert = f"INSERT INTO `{table_name}` ({', '.join(sql_fields + ['control_hash'])}) VALUES ({', '.join([f':{f}' for f in field_keys] + [':control_hash'])})"
    update = f"UPDATE `{table_name}` SET {', '.join([f'`{f}` = :{f}' for f in field_keys])} WHERE control_hash = :hash"
    check = f"SELECT 1 FROM `{table_name}` WHERE control_hash = :hash LIMIT 1"

    return {'insert': insert, 'update': update, 'check': check, 'fields': sql_fields}

def _convert_value(value: Any, column_type: str) -> Any:
    if value is None:
        return None

    if 'int' in column_type.lower():
        return int(value) if value is not None else 0
    elif 'decimal' in column_type.lower() or 'float' in column_type.lower():
        return float(value) if value is not None else 0.0
    elif 'date' in column_type.lower() or 'time' in column_type.lower():
        if isinstance(value, (date, datetime)):
            return value
        try:
            return datetime.strptime(str(value), '%Y-%m-%d')
        except ValueError:
            return None
    return str(value) if value is not None else ''

def _determine_column_type(field_name: str, value: Any, sample_records: List[Dict[str, Any]]) -> str:
    field_lower = field_name.lower()
    if field_lower in ['cuit', 'cuil', 'dni', 'codigo']:
        return "VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

    if isinstance(value, str):
        try:
            max_len = max(len(str(rec.get(field_name, ''))) for rec in sample_records)
            padding = 10
            if max_len + padding <= 255:
                return f"VARCHAR({max_len + padding}) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            return "TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        except Exception as e:
            logger.warning(f"Error calculando longitud para {field_name}: {str(e)}")
            return "TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    elif isinstance(value, int):
        return "BIGINT" if abs(value) > 2147483647 else "INT"
    elif isinstance(value, float):
        return "DECIMAL(15,2)"
    elif isinstance(value, (datetime, date)):
        return "DATETIME"
    elif isinstance(value, bool):
        return "BOOLEAN"
    return "TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
