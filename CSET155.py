import Modules.DBHelper as DBH

"""

This python file is meant to demonstrate the CRUD functionality of the DBHelper module
to satisfy the requirements of the CSET155 final project

if SQLAlchemy is not installed, open terminal and type: pip install -r requirements.txt

"""


# Step 1
# Establish connection and create database from .sql file
login = 'root'
password = 'cset155'
server = 'localhost'
db_name = 'ecom'
schema_path = 'ecommDB.sql'
conn = DBH.Conn(login, password, server, db_name, schema_path)

# Step 2
# Domonstrate CRUD functionality

# Read:
print("Example: SELECT from * user where user_id = 5")
column_names = conn._get_table("users").get_column_names()
results = conn.get_row("users", 5)
for i in range(len(column_names)):
    print(f"{column_names[i]}: {results[i]}")

