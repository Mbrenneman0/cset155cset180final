from Modules.Interface import Client

client = None

def init_client(app):
    global client

    client = Client(
        login=app.config['DB_LOGIN'],
        password=app.config['DB_PASSWORD'],
        server=app.config['DB_SERVER'],
        db_name=app.config['DB_NAME'],
        schema_path=app.config['SCHEMA_PATH']
    )