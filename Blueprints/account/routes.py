from flask import render_template, request, redirect, url_for, flash, Blueprint

# from Services."folder" import 'funcs_needed'

account_bp = Blueprint('account', __name__, url_prefix='/account')

@account_bp.route('/', methods=['GET'])
def account():
    return

@account_bp.route('/orders', methods=['GET'])
def view_acc_orders():
    return

@account_bp.route('/orders/<int:id>', methods=['GET'])
def view_order_details():
    return