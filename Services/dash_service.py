from flask import flash, session, request, render_template, redirect, url_for
import extensions
from .auth_service import check_credentials
from Modules.Types import TableNames, Role


def _set_order_quantity(quick_log: dict, order_items: list, user: Role) -> None:
    unique_orders = set(row['order_num'] for row in order_items)
    quick_log['orders'] = len(unique_orders)


def _set_revenue(quick_log: dict, order_items: list, user: Role) -> None:
    quick_log['revenue'] = sum(row['unit_price'] * row['qty'] for row in order_items)


def _set_product_quantity(quick_log: dict, user: Role) -> None:
    if user == Role.VENDOR:
        condition = f'vendor_id = {session["user_id"]}'
    else:
        condition = None
    products = extensions.client.conn.get_rows(TableNames.PRODUCTS, condition=condition)
    quick_log['products'] = len(products)


def _set_complaint_quantity(quick_log: dict, user: Role) -> None:
    if user == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]}'
    else:
        condition = None
    complaints = extensions.client.conn.get_rows(TableNames.COMPLAINTS,
                                                 join_tables=[TableNames.ORDER_ITEMS, TableNames.PRODUCTS],
                                                 condition=condition)
    quick_log['complaints'] = len(complaints)


def get_dashboard_data(user: Role) -> str:
    if not check_credentials(user.value, session.get('user_id')):
        flash('You do not have the necessary credentials', 'error')
        return redirect(url_for('index.index'))

    quick_log = {}
    graph_log = {}  # TODO: Populate with graph data if needed
    order_log = {}  # TODO: Populate with order details if needed

    if user == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]}'
    else:
        condition = None
    order_items = extensions.client.conn.get_rows(TableNames.ORDER_ITEMS,
                                                  join_tables=[TableNames.PRODUCTS],
                                                  condition=condition)

    _set_order_quantity(quick_log, order_items, user)
    _set_revenue(quick_log, order_items, user)
    _set_product_quantity(quick_log, user)
    _set_complaint_quantity(quick_log, user)

    return render_template('base_dashboard.html',
                           role=session['role'],
                           quick_log=quick_log,
                           graph_log=graph_log,
                           order_log=order_log)




