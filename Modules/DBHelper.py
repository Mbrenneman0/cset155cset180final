from sqlalchemy import create_engine, Connection, text
import os
from pathlib import Path

class Conn:

    class Table:
        def __init__(self, table_name:str, conn:Connection):
            self.table_name = table_name
            self.conn = conn
            if self._exists():
                self._load_columns()
                self._set_primarykey()

        def _exists(self) -> bool:
            query = "SHOW TABLES"
            rslt = self.conn.execute(text(query))
            return self.table_name in rslt.all()

        def _load_columns(self):
            query = f"""SHOW COLUMNS FROM {self.table_name}"""
            rslt = self.conn.execute(text(query))
            self.columns = list(rslt.all())

        def _set_primarykey(self):
            query = f"""SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE  TABLE_NAME = '{self.table_name}'
                    AND CONSTRAINT_NAME = 'PRIMARY'"""
            rslt = self.conn.execute(text(query))
            self.primary_key = rslt.first()
        # AIDEN_DEV
        def _set_foreignkeys(self):
            query = f"""SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_NAME = '{self.table_name}'
                    AND TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL"""
            rslt = self.conn.execute(text(query))
            self.foreign_keys = {row.COLUMN_NAME: {row.REFERENCED_TABLE_NAME: row.REFERENCED_COLUMN_NAME} for row in rslt}

        def get_foreign_key(self, fk_name = ''):
            
        # AIDEN_DEV

        def get_table_name(self, table_name_str):
            return self.table_name

        def get_all(self):

        def get_column_names():
          
        def select_columns(self, column_names:list[str]):

        def delete_row(self, pk_value:any):
            if type(pk_value) == str:
                pk_value = f"'{pk_value}'"
            query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = {pk_value}"
            self.conn.execute(text(query))

        def update_row(self, pk_value:any, data:dict):
            if type(pk_value) == str:
                pk_value = f"'{pk_value}'"
            columns = data.keys()
            items = []
            for column in columns:
                items.append(f"{column} = {data[column]}")
            set_txt = ', '.join(items)
            query = f"""UPDATE {self.table_name}
                    SET {set_txt}
                    WHERE {self.primary_key} = {pk_value}"""
            self.conn.execute(text(query))

        def get_row(self, pk_value, join_tables):
            if join_tables == []:
                query = f"SELECT * FROM {self.table_name} WHERE {pk_value} = {pk_value}"
            else:
                query = f"SELECT * FROM {self.table_name} WHERE {pk_value} = {pk_value} "
            self.conn.execute(text(query))

        def get_rows(self, condition, join_tables):
            if condition == '':
                query = f"SELECT * FROM {self.table_name}"
                self.conn.execute(text(query))
            else:
                query = f"SELECT * FROM {self.table_name} WHERE {condition}"
                self.conn.execute(text(query))
            
        def create_row(self, data:dict):
            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values})"
            self.conn.execute(text(query))

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
        for table_name in rslt.all():
            self.tables[table_name] = Table(table_name, self.conn)

    
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

    def _get_table(self, table_name:str) -> Table:
        for table in self.tables:
            if table_name in table.get_table_name(table_name):
                return table

    def query(self, query:str, data:dict={}):
        try:
            self.conn.execute(text(query, data))
        except Exception as e:
            print(e)

    def delete_row(self, table_name:str, pk_value:any):
        table = self._get_table(table_name)
        table.delete_row(pk_value)
      
    def create_row(self, table_name:str, data:dict):
        table = self._get_table(table_name)
        table.create_row(data)

    def get_row(self, table_name:str, pk_value:any, join_tables:list = []):
        table = self._get_table(table_name)
        table.get_row(pk_value, join_tables)

    def get_rows(self, table_name:str, condition:str = '', join_tables:list = []):
        table = self._get_table(table_name)
        table.get_row(condition, join_tables)
    

