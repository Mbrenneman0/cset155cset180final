from flask import Flask, render_template, request, redirect, url_for, flash
from Modules.Interface import Client

LOGIN = 'root'
PASSWORD = 'cset155'
SERVER = 'localhost'
DB_NAME = 'ecom'
SCHEMA_PATH = 'ecommDB.sql'

client = Client(LOGIN, PASSWORD, SERVER, DB_NAME, SCHEMA_PATH)
app = Flask(__name__)

# -------------- LOG IN / SIGN UP ---------------
@app.route('/login', methods=['GET', 'POST'])
def log_in():
    return

@app.route('/register', methods=['GET', 'POST'])
def register():
    return

@app.route('/venders/register', methods=['GET', 'POST'])
def vender_register():
    return

# -------------- PRODUCTS ---------------
@app.route('/products', methods=['GET', 'POST'])
def list_products():
    return render_template('index.html')

@app.route('/products/<int:id>', methods=['GET', 'POST'])
def product_detail(id):
    return

# -------------- ORDERS ---------------
@app.route('/order/<int:id>', methods=['GET','POST'])
def order(id):
    return

# ------------ ACCOUNT ------------------
@app.route('/account', methods=['GET','POST'])
def account():
    return

@app.route('/account/orders', methods=['GET','POST'])
def account_orders():
    return

@app.route('/account/orders/<int:id>', methods=['GET'])
def account_order_detail(id):
    return


if __name__ == '__main__':
    app.run(debug=True)
