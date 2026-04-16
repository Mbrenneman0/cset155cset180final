from flask import Blueprint

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def list_products():
    return "Products page"

@products_bp.route('/<int:id>')
def product_details():
    return