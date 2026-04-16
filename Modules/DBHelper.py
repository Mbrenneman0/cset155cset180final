from sqlalchemy import create_engine, Connection, text
import os
from pathlib import Path

class Conn:

    class Table:
        def __init__(self, parent, table_name:str, db_name:str, conn:Connection):
            self.parent = parent
            self.table_name = table_name
            self.db_name = db_name
            self.conn = conn
            self.exists = self._exists()
            if self.exists:
                self._load_columns()
                self._set_primarykey()
                self._set_foreignkeys()

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
            primary_keys = list(rslt.scalars().all())
            if len(primary_keys) == 0:
                self.primary_keys = None
            else:
                self.primary_keys = primary_keys
            
        def _set_foreignkeys(self):
            query = f"""SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_NAME = '{self.table_name}'
                    AND TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL"""
            rslt = self.conn.execute(text(query))
            self.foreign_keys = {row.COLUMN_NAME: {'table': row.REFERENCED_TABLE_NAME, 'column': row.REFERENCED_COLUMN_NAME} for row in rslt}

        def _where_clause_from_pk(self):
            where_clause = " AND ".join([f"{self.table_name}.{col} = :{col}" for col in self.primary_keys])
            return where_clause
        
        def _normalize_pk_value(self, pk_value) -> dict:
            if not self.primary_keys:
                raise ValueError(f"Table {self.table_name} has no primary key")
            if type(pk_value) == dict:
                if set(pk_value.keys()) != set(self.primary_keys):
                    raise ValueError(
                        f"Expected primary key fields {self.primary_keys}"
                    )
                return {key: pk_value[key] for key in self.primary_keys}
            
            if len(self.primary_keys) == 1:
                if isinstance(pk_value, (tuple, list)):
                    if len(pk_value) != 1:
                        raise ValueError(
                            f"Table {self.table_name} expects 1 primary key value"
                        )
                    return {self.primary_keys[0]: pk_value[0]}
                return {self.primary_keys[0]: pk_value}
            
            if isinstance(pk_value, (tuple, list)):
                if len(pk_value) != len(self.primary_keys):
                    raise ValueError(
                        f"Table {self.table_name} expects {len(self.primary_keys)} primary key values "
                        f"{self.primary_keys}, got {len(pk_value)}")
                return dict(zip(self.primary_keys, pk_value))
            raise ValueError(
                f"Table {self.table_name} expects primary key values for {self.primary_keys}. "
                f"Use tuple, list, or dict.")

        def _build_joins(self, join_tables):
            joins = []
            i = 0

            for join_name in join_tables:

                join_table = self.parent._get_table(join_name)
                found = False
                
                for fk_col, ref in join_table.foreign_keys.items():
                    if ref['table'] == self.table_name:
                            joins.append(
                                f"JOIN {join_table.table_name} "
                                f"ON {join_table.table_name}.{fk_col} = "
                                f"{self.table_name}.{ref['column']}"
                            )
                            found = True
                            break
                    if found:
                        break

                i+=1
                for join_name in join_tables[:i-1]:

                    ref_table = self.parent._get_table(join_name)
                    found = False

                    for fk_col, ref in join_table.foreign_keys.items():
                        if ref['table'] == ref_table.table_name:
                            joins.append(
                                f"JOIN {join_table.table_name} "
                                f"ON {join_table.table_name}.{fk_col} = "
                                f"{join_name}.{ref['column']}"
                            )
                            found = True
                            break
                    if found:
                        break
                    
                if not found:
                    raise ValueError(f"Could not join {join_name} to current query")

            return " ".join(joins)

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
            params = self._normalize_pk_value(pk_value)
            query = f"DELETE FROM {self.table_name} WHERE {self._where_clause_from_pk()}"
            self.conn.execute(text(query), params)
            self.conn.commit()

        def update_row(self, pk_value, data: dict):
            params = self._normalize_pk_value(pk_value)
            params.update(data)
            set_txt = ', '.join([f"{col} = :{col}" for col in data.keys()])
            query = f"""UPDATE {self.table_name}
                    SET {set_txt}
                    WHERE {self._where_clause_from_pk()}
                    """
            self.conn.execute(text(query), params)
            self.conn.commit()

        def get_row(self, pk_value, join_tables):
            params = self._normalize_pk_value(pk_value)
            base = self
            if join_tables is None:
                query = f"SELECT * FROM {self.table_name} WHERE {self._where_clause_from_pk()}"
            else:
                join_sql = self._build_joins(base, join_tables)
                query = f"SELECT * FROM {self.table_name} {join_sql} WHERE {self._where_clause_from_pk()}"
            rslt = self.conn.execute(text(query), params)
            row = rslt.mappings().first()
            return dict(row) if row else None  

        def get_rows(self, condition, join_tables, params:dict = {}):
            if join_tables is None:
                query = f"SELECT * FROM {self.table_name}"
            else:
                join_sql = self._build_joins(join_tables)
                query = f"SELECT * FROM {self.table_name} {join_sql}"
            if condition:
                query += f" WHERE {condition}"
            rslt = self.conn.execute(text(query), params)
            return [dict(row) for row in rslt.mappings().all()]    
            
        def create_row(self, data: dict):
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f":{key}" for key in data.keys()])
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            self.conn.execute(text(query), data)
            self.conn.commit()

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
            self.tables[table_name] = Conn.Table(self, table_name, self.db_name, self.conn)

    
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
                    print('\n\nTESTING',conditions,'\n\n')
                    print('\n\nTESTING',statement,'\n\n')
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

    def update_row(self, table_name:str, pk_value:any, data:dict):
        table = self._get_table(table_name)
        table.update_row(pk_value, data)

    def get_row(self, table_name:str, pk_value:any, join_tables:list = None):
        table = self._get_table(table_name)
        rslt = table.get_row(pk_value, join_tables)
        return rslt

    def get_rows(self, table_name:str, condition:str = None, join_tables:list = None, params:dict = {}):
        table = self._get_table(table_name)
        rslt = table.get_rows(condition, join_tables, params)
        return rslt
    

