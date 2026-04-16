from flask import render_template, request, redirect, url_for, flash, Blueprint

# from Services."folder" import 'funcs_needed'

account_bp = Blueprint('account', __name__, url_prefix='/account')

@account_bp.route('/')
def account():
    return

@account_bp.route('/orders')
def view_acc_orders():
    return

@account_bp.route('/orders/<int:id>')
def view_order_details():
    return