from flask import flash, session, request, render_template, redirect, url_for
import extensions
from .auth_service import check_credentials
from Modules.Types import TableNames, Role
from datetime import datetime


def _get_order_quantity(order_items: list) -> int:
    unique_orders = set(row['order_num'] for row in order_items)
    return len(unique_orders)

def _get_revenue(order_items: list) -> float:
    return sum(row['unit_price'] * row['qty'] for row in order_items)

def _get_product_quantity(user: Role) -> int:
    if user == Role.VENDOR:
        condition = f'vendor_id = {session["user_id"]}'
    else:
        condition = None
    products = extensions.client.conn.get_rows(TableNames.PRODUCTS.value, condition=condition)
    return len(products)

def _get_complaint_quantity(user: Role) -> int:
    if user == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]}'
    else:
        condition = None
    complaints = extensions.client.conn.get_rows(TableNames.PRODUCTS.value,
                                                join_tables=[TableNames.COMPLAINTS.value],
                                                condition=condition)
    print(complaints)
    return len(complaints)

def _get_monthly_revenue(user: Role) -> dict:
    current_year = datetime.now().year
    keys = [f'{current_year}-{month:02d}' for month in range(1, 13)]
    month_map = {key: 0 for key in keys}
    if user == Role.VENDOR:
        condition = (
            f"products.vendor_id = {session['user_id']} AND "
            f"orders.order_time >= '{current_year}-01-01' AND "
            f"orders.order_time < '{current_year+1}-01-01'"
        )
    else:
        condition = (
            f"orders.order_time >= '{current_year}-01-01' AND "
            f"orders.order_time < '{current_year+1}-01-01'"
        )

    rows = extensions.client.conn.get_rows(TableNames.ORDERS.value,
                                          join_tables=[TableNames.ORDER_ITEMS.value,TableNames.PRODUCTS.value],
                                          condition=condition)
    print('\n\n',rows,'\n\n')


    for row in rows:
        order_time = row.get('order_time')
        if not order_time:
            continue
        order_time = datetime.strptime(order_time, '%Y-%m-%d %H:%M:%S')
        month_key = order_time.strftime('%Y-%m')
        if month_key in month_map:
            month_map[month_key] += float(row.get('unit_price', 0)) * float(row.get('qty', 0))

    return {datetime.strptime(key, '%Y-%m').strftime('%b') : month_map[key] for key in keys}


def get_dashboard_data(user: Role) -> str:
    if not check_credentials(user.value, session.get('user_id')):
        flash('You do not have the necessary credentials', 'error')
        return redirect(url_for('index.index'))

    quick_log = {}
    graph_log = {}
    order_log = {}  # TODO: Populate with order details if needed

    if user == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]}'
    else:
        condition = None
    order_items = extensions.client.conn.get_rows(TableNames.PRODUCTS.value,
                                                  join_tables=[TableNames.ORDER_ITEMS.value],
                                                  condition=condition)
    print(order_items)

    quick_log['orders'] = _get_order_quantity(order_items)
    quick_log['revenue'] = _get_revenue(order_items)
    quick_log['products'] = _get_product_quantity(user)
    quick_log['complaints'] = _get_complaint_quantity(user)

    graph_log['ytd_rev'] = _get_monthly_revenue(user)

    return render_template('base_dashboard.html',
                           role=session['role'],
                           quick_log=quick_log,
                           graph_log=graph_log,
                           order_log=order_log)




