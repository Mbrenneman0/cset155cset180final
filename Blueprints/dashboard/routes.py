from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from Modules.Types import Role
from Services.dash_service import get_dashboard_data, update_product_status

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
    print(role)
    return


def test(role, id):
    session['role'] = role
    session['user_id'] = id