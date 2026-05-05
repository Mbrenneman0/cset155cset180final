from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from Modules.Types import Role
from Services.dash_service import get_dashboard_data

dash_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dash_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))
    role = session.get('role')
    if role == Role.VENDOR:
        return redirect(url_for('dashboard.vendor_dash'))
    elif role == Role.ADMIN:
        return redirect(url_for('dashboard.admin_dash'))
    elif role == Role.CUSTOMER:
        return redirect(url_for('dashboard.cust_dash'))
    else:
        flash('Invalid user role. Please log in again.')
        return redirect(url_for('index.index'))

# ------------ MAIN DASH ----------------
@dash_bp.route('/vendor')
def vendor_dash():
    return get_dashboard_data(Role.VENDOR)

@dash_bp.route('/admin')
def admin_dash():
    return get_dashboard_data(Role.ADMIN)

@dash_bp.route('/account')
def cust_dash():
    return get_dashboard_data(Role.CUSTOMER)

# @dash_bp.route('/admin/vender')
# def admin_dash():
#     return render_template('base_dashboard.html')

# ----- PRODUCTS ------
@dash_bp.route('/<role>/products')
def view_products(role):
    print(role)
    return


def test(role, id):
    session['role'] = role
    session['user_id'] = id