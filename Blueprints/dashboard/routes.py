from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from Modules.Types import TableNames, Role
from Services.dash_service import get_dashboard_data

dash_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dash_bp.route('/vendor')
def vendor_dash():
    test(Role.VENDOR, 9)
    get_dashboard_data(Role.VENDOR)

@dash_bp.route('/admin')
def admin_dash():
    test(Role.ADMIN, 1)
    get_dashboard_data(Role.ADMIN)

# @dash_bp.route('/admin/vender')
# def admin_dash():
#     return render_template('base_dashboard.html')


def test(role, id):
    session['role'] = role
    session['user_id'] = id