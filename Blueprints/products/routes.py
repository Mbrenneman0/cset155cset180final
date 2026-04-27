from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from Services.product_service import get_product

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/', methods=['GET'])
def list_products():
    return "Products page"

@products_bp.route('/view_product/<string:sku>', methods=['GET'])
def view_product(sku):
    product = get_product(sku, with_imgs=True, with_reviews=True)
    if not product:
        flash('Product not found')
        return redirect(url_for('index.index'))
    return render_template('prod_page.html', product=product)

@products_bp.route('/add_review/<string:sku>', methods=['POST'])
def add_review(sku):
    # change return to page for review submission form
    # review submission form will redirect back to view product page after submission
    return redirect(url_for('products.view_product', sku=sku))