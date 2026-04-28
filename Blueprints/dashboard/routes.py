from flask import render_template, request, redirect, url_for, flash, Blueprint

# from Services."folder" import 'funcs_needed'

dash_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dash_bp.route('/vendor')
def vendor_dash():
    return render_template('base_dashboard.html')

@dash_bp.route('/admin')
def admin_dash():
    return render_template('base_dashboard.html')

# @dash_bp.route('/admin/vender')
# def admin_dash():
#     return render_template('base_dashboard.html')