from dbf_updater import dbf_updater



dbf_updater = DBFUpdater(
    ssh_host=os.getenv('SSH_HOST'),
    ssh_port=int(os.getenv('SSH_PORT', 22)),
    ssh_user=os.getenv('SSH_USER'),
    ssh_password=os.getenv('SSH_PASSWORD'),
    remote_path=os.getenv('REMOTE_DBF_PATH'),
    local_path=os.getenv('LOCAL_DBF_PATH'),
    use_db_logging=os.getenv('USE_DB_LOGGING', 'True').lower() == 'true'
)

# Llamar a la actualización
resultado = dbf_updater.actualizardbfoficina()
if resultado:
    print("Actualización completada con éxito")
else:
    print("Hubo problemas durante la actualización")