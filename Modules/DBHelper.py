from sqlalchemy import create_engine, Connection, text
import os
from pathlib import Path

class Conn:

    class Table:
        def __init__(self, table_name:str, db_name:str, conn:Connection):
            self.table_name = table_name
            self.db_name = db_name
            self.conn = conn
            self.exists = self._exists()
            if self.exists:
                self._load_columns()
                self._set_primarykey()

        def _exists(self) -> bool:
            query = "SHOW TABLES"
            rslt = self.conn.execute(text(query))
            return self.table_name in [row[0] for row in rslt.all()]

        def _load_columns(self):
            query = f"""SHOW COLUMNS FROM {self.table_name}"""
            rslt = self.conn.execute(text(query))
            self.columns = list(rslt.all())

        def _set_primarykey(self):
            query = text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = :db_name
                  AND TABLE_NAME = :table_name
                  AND CONSTRAINT_NAME = 'PRIMARY'
                ORDER BY ORDINAL_POSITION
            """)
            rslt = self.conn.execute(query, {
                "db_name": self.db_name,
                "table_name": self.table_name
            })
            self.primary_key = rslt.scalar()

        def get_all(self) -> list[dict]:
            query = f"""SELECT * FROM {self.table_name}"""
            rslt = self.conn.execute(text(query))
            output = [dict(row) for row in rslt.mappings().all()]
            return output

        def get_column_names(self) -> list[str]:
            query = f"SHOW COLUMNS FROM {self.table_name}"
            rslt = self.conn.execute(text(query))
            return rslt.scalars().all()
          
        def select_columns(self, column_names:list[str]) -> list[dict]:
            columns_list = ', '.join(column_names)
            query = f"""SELECT {columns_list} FROM {self.table_name}"""
            rslt = self.conn.execute(text(query))
            output = [dict(row) for row in rslt.mappings().all()]
            return output

        def delete_row(self, pk_value:any):
            if type(pk_value) == str:
                pk_value = f"'{pk_value}'"
            query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = {pk_value}"
            self.conn.execute(text(query))

        def update_row(self, pk_value, data: dict):
            set_txt = ', '.join([f"{col} = :{col}" for col in data.keys()])
            query = f"""UPDATE {self.table_name}
                    SET {set_txt}
                    WHERE {self.primary_key} = :pk
                    """
            params = dict(data)
            params["pk"] = pk_value
            self.conn.execute(text(query), params)
            self.conn.commit()

        def get_row(self, pk_value):
            query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = {pk_value}"
            rslt = self.conn.execute(text(query))
            return rslt.fetchone()

        def get_rows(self, condition):
            if condition == '':
                query = f"SELECT * FROM {self.table_name}"
                rslt = self.conn.execute(text(query))
            else:
                query = f"SELECT * FROM {self.table_name} WHERE {condition}"
                rslt = self.conn.execute(text(query))
            return rslt.all()    
            
        def create_row(self, data: dict):
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f":{key}" for key in data.keys()])
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            self.conn.execute(text(query), data)

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

        self.tables = {}
        query = "SHOW TABLES"
        rslt = self.conn.execute(text(query))
        for row in rslt.all():
            table_name = row[0]
            self.tables[table_name] = Conn.Table(table_name, self.db_name, self.conn)

    
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
                    conditions = [
                        "CREATE DATABASE" not in statement.upper(),
                        "USE " not in statement.upper(),
                        "DROP DATABASE" not in statement.upper()
                    ]
                    if all(conditions):
                        conn.execute(text(statement))

    def _get_table(self, table_name:str) -> Table:
                return self.tables.get(table_name)

    def query(self, query:str, data:dict={}):
        try:
            self.conn.execute(text(query), data)
        except Exception as e:
            print(e)

    def delete_row(self, table_name:str, pk_value:any):
        table = self._get_table(table_name)
        table.delete_row(pk_value)
      
    def create_row(self, table_name:str, data:dict):
        table = self._get_table(table_name)
        table.create_row(data)

    def get_row(self, table_name:str, pk_value:any):
        table = self._get_table(table_name)
        return table.get_row(pk_value)

    def get_rows(self, table_name:str, condition:str = ''):
        table = self._get_table(table_name)
        return table.get_rows(condition)
    

