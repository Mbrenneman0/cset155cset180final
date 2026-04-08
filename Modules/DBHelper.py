from sqlalchemy import create_engine, Connection, text
import os
from pathlib import Path

class Conn():
    def __init__(self, login:str,
                 password:str,
                 server:str,
                 db_name:str,
                 schema_path:str ='scripts/sql/schema.sql'):
        self.login = login
        self.password = password
        self.server = server
        self.db_name = db_name
        base_dir = Path.cwd()
        self.schema_path = os.path.join(base_dir, schema_path)

        if not self._db_exists():
            self._create_db()

        connection_str = f"mysql://{self.login}:{self.password}@{self.server}/{self.db_name}"
        engine = create_engine(connection_str, echo=True, connect_args={"local_infile":1})
        self.conn = engine.connect()
    
    def _db_exists(self) -> bool:
        connection_str = f"mysql://{self.login}:{self.password}@{self.server}"
        engine = create_engine(connection_str, echo=True, connect_args={"local_infile":1})
        with engine.connect() as conn:
            result = conn.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result.fetchall()]
        engine.dispose()
        return self.db_name in databases
    
    def _create_db(self):
        connection_str = f"mysql://{self.login}:{self.password}@{self.server}"
        engine = create_engine(connection_str, echo=True, connect_args={"local_infile":1})
        with engine.begin() as conn:
            conn.execute(text(f"CREATE DATABASE {self.db_name}"))
        engine.dispose()
        connection_str = f"mysql://{self.login}:{self.password}@{self.server}/{self.db_name}"
        engine = create_engine(connection_str, echo=True, connect_args={"local_infile":1})
        with engine.connect() as conn:
            try:
                self._create_tables(conn)
            except Exception as e:
                print(e)
        engine.dispose()

    def _create_tables(self, conn:Connection):
        if not Path(self.schema_path).is_file():
            raise FileNotFoundError(f".sql file not found at: {self.schema_path}")
        else:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                sql = f.read()
            statements = [statement.strip() for statement in sql.split(';') if statement.strip()]
            with conn.begin():
                for statement in statements:
                    if "CREATE DATABASE" not in statement.upper() and "USE" not in statement.upper():
                        conn.execute(text(statement))


    