import Modules.DBHelper as DBH

"""

This python file is meant to demonstrate the CRUD functionality of the DBHelper module
to satisfy the requirements of the CSET155 final project

if SQLAlchemy is not installed, open terminal and type: pip install -r requirements.txt

Make sure to delete ecom database with "DROP DATABASE ecom" each time this is ran.

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

print("\n\n")

# Write:
print("Examle: Insert Product")
prod_data = {
    "sku": "R-V8C",
    "qty": 50,
    "title": "V8 Camaro",
    "color": "Red",
    "size": "Large",
    "description": "Goes fast",
    "unit_price": 42000,
    "warranty_period": "5 years",
    "vender_id": 8
}
conn.create_row("product", prod_data)
print("New product added: ")

column_names = conn._get_table("product").get_column_names()
results = conn.get_row("product", "'R-V8C'")
for i in range(len(column_names)):
    print(f"{column_names[i]}: {results[i]}")

# Update:
print("Color changed to blue: ")
conn._get_table("product").update_row("R-V8C", {'color': "Blue"})

column_names = conn._get_table("product").get_column_names()
results = conn.get_row("product", "'R-V8C'")
for i in range(len(column_names)):
    print(f"{column_names[i]}: {results[i]}")

# Delete: 
print("Delte row:")
conn.delete_row("users", 5)

column_names = conn._get_table("users").get_column_names()
results = conn.get_rows("users")
for row in results:
    for i in range(len(column_names)):
        print(f"{column_names[i]}: {row[i]}")