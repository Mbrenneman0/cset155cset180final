from flask import render_template, request, redirect, session, url_for, flash, Blueprint
from Services.account_service import acct_route

account_bp = Blueprint('account', __name__, url_prefix='/account')

@account_bp.route('/', methods=['GET'])
def account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    else:
        try:
            return redirect(url_for(acct_route(session['user_id'])))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index.index'))

@account_bp.route('/orders', methods=['GET'])
def view_acc_orders():
    return

@account_bp.route('/orders/<int:id>', methods=['GET'])
def view_order_details():
    return