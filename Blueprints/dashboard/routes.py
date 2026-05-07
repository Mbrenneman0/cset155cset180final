from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from Modules.Types import Role
from Services.dash_service import get_dashboard_data, update_product_status, get_order_log
from Services.product_service import get_products, get_product, update_product

dash_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dash_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))
    role = session.get('role')
    if role in [Role.VENDOR.value, Role.ADMIN.value, Role.CUSTOMER.value]:
        return redirect(url_for(f'dashboard.{role.lower()}_dash'))
    else:
        flash('Invalid user role. Please log in again.')
        return redirect(url_for('index.index'))

# ------------ MAIN DASH ----------------
@dash_bp.route('/vendor', methods=['GET','POST'])
def vendor_dash():
    if request.method == 'POST':
        update_product_status(dict(request.form))
    return get_dashboard_data(Role.VENDOR)

@dash_bp.route('/admin', methods=['GET','POST'])
def admin_dash():
    if request.method == 'POST':
        update_product_status(dict(request.form))
    return get_dashboard_data(Role.ADMIN)

@dash_bp.route('/account')
def customer_dash():
    return get_dashboard_data(Role.CUSTOMER)


# ----- PRODUCTS ------
@dash_bp.route('/<role>/products')
def view_products(role):
    products = get_products(with_imgs=True)
    if role == Role.VENDOR.value:
        products = [product for product in products if product['vendor_id'] == session['user_id']]
    return render_template('dash_products.html', products= products, role= role, active_page = 'products')


@dash_bp.route('/<string:role>/products/<string:sku>/edit', methods=['GET', 'POST'])
def edit_product(role, sku):
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))

    product = get_product(sku, with_imgs=True)

    if role == Role.VENDOR.value and product['vendor_id'] != session['user_id']:
        flash("You cannot edit another vendor's product.", "error")
        return redirect(url_for('dashboard.view_products', role=role))

    if request.method == 'POST':
        update_product(
            request.form,
            new_images=request.files.getlist('images'),
            delete_images=request.form.getlist('delete_images')
        )
        flash('Product updated successfully.', 'info')
        return redirect(url_for('dashboard.view_products', role=role))

    return render_template(
        'dash_edit_product.html',
        product=product,
        role=role
    )
    

def test(role, id):
    session['role'] = role
    session['user_id'] = id

    
# ----- ORDERS -------
@dash_bp.route('/<role>/orders', methods=['GET','POST'])
def view_orders(role):
    if request.method == 'POST':
        update_product_status(dict(request.form))
    return render_template('dash_orders.html', role=role, order_log=get_order_log(session['role']))
@dash_bp.route('/<role>/orders/<action>', methods=['GET','POST'])
def view_filtered_orders(role, action):
    if request.method == 'POST':
        update_product_status(dict(request.form))
    return render_template('dash_orders.html', role=role, order_log=get_order_log(session['role'], action))
