from flask import Flask, render_template, request, redirect, url_for, flash
from Modules.Interface import *

LOGIN = 'root'
PASSWORD = 'cset155'
SERVER = 'localhost'
DB_NAME = 'ecom'
SCHEMA_PATH = 'ecommDB.sql'

client = Client(LOGIN, PASSWORD, SERVER, DB_NAME, SCHEMA_PATH)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
