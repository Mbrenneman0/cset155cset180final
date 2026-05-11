"""
Instructions:
    1. Make sure there is no SQL database named ecom

    2. Make sure your MySQL credentials are entered in config.py

    3. Run the following command in a python terminal from the project root folder:
            pip install -r requirements.txt

    4. Run main.py and open http://127.0.0.1:5000/ in a browser
            The database will be created and initialized automatically when main is ran
"""
from flask import Flask
from config import Config

from Blueprints.index import index_bp
from Blueprints.auth import auth_bp
from Blueprints.products import products_bp
from Blueprints.cart import cart_bp
from Blueprints.orders import orders_bp
from Blueprints.account import account_bp
from Blueprints.dashboard import dash_bp

from extensions import init_client

def create_app():
    app = Flask(__name__, static_folder='Static')
    app.secret_key = 'secret_key'
    app.config.from_object(Config)

    init_client(app)

    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(dash_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
