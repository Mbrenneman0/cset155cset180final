from flask import Flask
from config import Config

from Blueprints.auth import auth_bp
from Blueprints.products import products_bp
from Blueprints.cart import cart_bp
from Blueprints.orders import orders_bp
from Blueprints.account import account_bp

from extensions import init_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_client(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(account_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
