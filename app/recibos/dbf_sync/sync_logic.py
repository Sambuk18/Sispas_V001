import logging
from datetime import datetime
from pathlib import Path
from flask import current_app
from .dbf_utils import read_dbf
from .db_utils import create_table_from_dbf, insert_records

logger = logging.getLogger(__name__)

def sync_dbf_to_mariadb():
    from app import db  # Importa SQLAlchemy db ya configurado

    dbf_folder = current_app.config.get('DBF_FOLDER', './dbf')
    dbf_files = current_app.config.get('DBF_FILES', [])

    total_inserted = 0
    error_list = []

    for file_name in dbf_files:
        try:
            file_path = Path(dbf_folder) / file_name
            if not file_path.exists():
                logger.warning(f"Archivo no encontrado: {file_name}")
                continue

            table_name = file_name.replace('.dbf', '').lower()

            create_table_from_dbf(db.engine, file_name, force_recreate=False)

            records = read_dbf(file_name)
            if not records:
                continue

            inserted, _, errors = insert_records(db.engine, table_name, records)  # corregido
            total_inserted += inserted
            error_list.extend(errors)

        except Exception as e:
            logger.error(f"Error procesando {file_name}: {str(e)}")
            error_list.append(str(e))

    return {
        "total_inserted": total_inserted,
        "errors": error_list,
        "timestamp": datetime.now().isoformat()
    }
