from flask import Flask, render_template, request, redirect, session, url_for, flash, Blueprint
import Services.cart_service as Cart_Service

cart_bp = Blueprint('cart',__name__,url_prefix='/cart')

@cart_bp.route('/', methods=['GET'])
def view_cart():
    items = Cart_Service.get_cart_items()
    return render_template('cart.html', items=items)

@cart_bp.route("/update_cart_qty", methods=["POST"])
def update_cart_qty():
    sku = request.form.get("sku")
    action = request.form.get("action")
    qty = int(request.form.get("qty", 1))

    try:
        Cart_Service.update_cart_qty(sku, action, qty)
    except Exception as e:
        if str(e) == "Not logged in":
            flash('You must be logged in to update your cart', 'error')
            return redirect(url_for('account.login'))
        flash(str(e), 'error')

    return redirect(request.referrer)

@cart_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    sku = request.form.get('sku')
    try:
        Cart_Service.add_item_to_cart(sku)
    except Exception as e:
        if str(e) == "Not logged in":
            flash('You must be logged in to add items to your cart', 'error')
            return redirect(url_for('account.login'))
        flash(str(e), 'error')
        return redirect(request.referrer)
    flash('Item added to cart!', 'info')
    return redirect(request.referrer)

@cart_bp.route('/remove_item', methods=['POST'])
def remove_item():
    sku = request.form.get('sku')
    try:
        Cart_Service.remove_item_from_cart(sku)
    except Exception as e:
        if str(e) == "Not logged in":
            flash('You must be logged in to update your cart', 'error')
            return redirect(url_for('account.login'))
        flash(str(e), 'error')
    return redirect(request.referrer)