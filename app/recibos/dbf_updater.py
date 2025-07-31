# file: dbf_updater.py
import os
import paramiko
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar SQLAlchemy
db = SQLAlchemy()

class DBFUpdater:
    def __init__(self, use_db_logging=None):
        """
        Inicializa el actualizador de archivos DBF usando variables de entorno
        
        Args:
            use_db_logging (bool): Opcional. Si None, usa valor de .env
        """
        # Cargar configuraciones desde variables de entorno
        self.ssh_host = os.getenv('SSH_HOST')
        self.ssh_port = int(os.getenv('SSH_PORT', '22'))  # Default 22 si no está definido
        self.ssh_user = os.getenv('SSH_USER')
        self.ssh_password = os.getenv('SSH_PASSWORD')
        self.ssh_key_path = os.getenv('SSH_KEY_PATH')
        self.remote_path = os.getenv('REMOTE_DBF_PATH')
        self.local_path = os.getenv('LOCAL_DBF_PATH')
        
        # Determinar si usamos DB para logging (default True)
        env_logging = os.getenv('USE_DB_LOGGING', 'True').lower() == 'true'
        self.use_db_logging = use_db_logging if use_db_logging is not None else env_logging
        
        # Validar configuraciones requeridas
        required_settings = {
            'SSH_HOST': self.ssh_host,
            'SSH_USER': self.ssh_user,
            'REMOTE_DBF_PATH': self.remote_path,
            'LOCAL_DBF_PATH': self.local_path
        }
        
        missing = [name for name, value in required_settings.items() if not value]
        if missing:
            raise ValueError(f"Faltan configuraciones requeridas en .env: {', '.join(missing)}")
            
        # Asegurar que existe el directorio local
        os.makedirs(self.local_path, exist_ok=True)
        
        # Configurar logging a archivo si no se usa DB
        if not self.use_db_logging:
            self.log_file = os.path.join(self.local_path, 'dbf_update.log')
    
    def _log_operation(self, filename, operation, details=""):
        """Registra una operación en el sistema de logging configurado"""
        timestamp = datetime.utcnow()
        
        if self.use_db_logging:
            log_entry = DBFUpdateLog(
                filename=filename,
                operation=operation,
                details=details
            )
            db.session.add(log_entry)
            db.session.commit()
        else:
            log_message = f"[{timestamp}] {operation.upper()} - {filename}"
            if details:
                log_message += f" - {details}"
            
            with open(self.log_file, 'a') as f:
                f.write(log_message + "\n")
    
    def _get_ssh_connection(self):
        """Establece y retorna una conexión SSH usando credenciales del .env"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Autenticación por clave o por password
            if self.ssh_key_path and os.path.exists(self.ssh_key_path):
                private_key = paramiko.RSAKey.from_private_key_file(self.ssh_key_path)
                ssh.connect(
                    hostname=self.ssh_host,
                    port=self.ssh_port,
                    username=self.ssh_user,
                    pkey=private_key
                )
            else:
                if not self.ssh_password:
                    raise ValueError("Se requiere SSH_PASSWORD o SSH_KEY_PATH válido en .env")
                ssh.connect(
                    hostname=self.ssh_host,
                    port=self.ssh_port,
                    username=self.ssh_user,
                    password=self.ssh_password
                )
            return ssh
        except Exception as e:
            self._log_operation("SYSTEM", "error", f"SSH Connection failed: {str(e)}")
            raise
    
    def _get_sftp_connection(self):
        """Establece y retorna una conexión SFTP"""
        ssh = self._get_ssh_connection()
        return ssh.open_sftp()
    
    def _should_update_file(self, remote_file, local_file):
        """Determina si un archivo necesita ser actualizado"""
        if not os.path.exists(local_file):
            return True
        
        remote_mtime = remote_file.st_mtime
        local_mtime = os.path.getmtime(local_file)
        
        return remote_mtime > local_mtime
    
    def actualizardbfoficina(self):
        """
        Actualiza los archivos .dbf desde el servidor remoto, copiando solo
        los archivos que han sido modificados.
        """
        sftp = None
        try:
            sftp = self._get_sftp_connection()
            sftp.chdir(self.remote_path)
            
            # Listar archivos .dbf en el directorio remoto
            remote_files = [f for f in sftp.listdir_attr() if f.filename.lower().endswith('.dbf')]
            
            if not remote_files:
                self._log_operation("SYSTEM", "info", "No se encontraron archivos .dbf en el directorio remoto")
                return False
            
            update_count = 0
            skip_count = 0
            
            for file_attr in remote_files:
                remote_filename = file_attr.filename
                remote_path = os.path.join(self.remote_path, remote_filename)
                local_path = os.path.join(self.local_path, remote_filename)
                
                try:
                    if self._should_update_file(file_attr, local_path):
                        sftp.get(remote_path, local_path)
                        self._log_operation(
                            remote_filename, 
                            "copied", 
                            f"Tamaño: {file_attr.st_size} bytes"
                        )
                        update_count += 1
                    else:
                        self._log_operation(
                            remote_filename, 
                            "skipped", 
                            "No hay cambios desde la última actualización"
                        )
                        skip_count += 1
                except Exception as e:
                    self._log_operation(
                        remote_filename, 
                        "error", 
                        f"Error al procesar archivo: {str(e)}"
                    )
            
            self._log_operation(
                "SYSTEM", 
                "summary", 
                f"Actualizados: {update_count}, Saltados: {skip_count}, Total: {len(remote_files)}"
            )
            
            return True
            
        except Exception as e:
            self._log_operation("SYSTEM", "error", f"Error general: {str(e)}")
            return False
        finally:
            if sftp:
                sftp.close()