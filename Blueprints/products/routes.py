from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from Services.product_service import get_product

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/', methods=['GET'])
def list_products():
    return "Products page"

@products_bp.route('/view_product/<string:sku>', methods=['GET'])
def view_product(sku):
    product = get_product(sku, with_imgs=True, with_reviews=True, with_rating=True)
    if not product:
        flash('Product not found')
        return redirect(url_for('index.index'))
    return render_template('prod_page.html', product=product)