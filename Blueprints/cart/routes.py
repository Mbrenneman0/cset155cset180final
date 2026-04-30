from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from Services.cart_service import add_item_to_cart, get_cart_items

cart_bp = Blueprint('cart',__name__,url_prefix='/cart')

@cart_bp.route('/', methods=['GET'])
def view_cart():
    items = get_cart_items()
    return render_template('cart.html', items=items)

@cart_bp.route('/add', methods=['POST'])
def add_item():
    return

@cart_bp.route('/remove', methods=['POST'])
def remove_item():
    return

@cart_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    sku = request.form.get('sku')
    try:
        add_item_to_cart(sku)
    except Exception as e:
        if str(e) == "Not logged in":
            flash('You must be logged in to add items to your cart', 'error')
            return redirect(url_for('account.login'))
        flash(str(e), 'error')
        return redirect(request.referrer)
    flash('Item added to cart!', 'info')
    return redirect(request.referrer)