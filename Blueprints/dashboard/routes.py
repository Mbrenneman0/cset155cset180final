from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from Modules.Types import TableNames, Role
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

@dash_bp.route('/vendor')
def vendor_dash():
    test(Role.VENDOR, 8)
    return get_dashboard_data(Role.VENDOR)

@dash_bp.route('/admin')
def admin_dash():
    test(Role.ADMIN, 1)
    return get_dashboard_data(Role.ADMIN)

@dash_bp.route('/account')
def cust_dash():
    test(Role.CUSTOMER, 7)
    return get_dashboard_data(Role.CUSTOMER)

# @dash_bp.route('/admin/vender')
# def admin_dash():
#     return render_template('base_dashboard.html')


def test(role, id):
    session['role'] = role
    session['user_id'] = id