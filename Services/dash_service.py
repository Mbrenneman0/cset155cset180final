from flask import flash, session, request, render_template, redirect, url_for
import extensions
from .auth_service import check_credentials
from Modules.Types import *
from datetime import datetime


def _get_order_quantity(order_items: list) -> int:
    unique_orders = set(row['order_num'] for row in order_items)
    return len(unique_orders)

def _get_revenue(order_items: list) -> float:
    return sum(row['unit_price'] * row['qty'] for row in order_items)

def _get_product_quantity(role: Role) -> int:
    if role == Role.VENDOR:
        condition = f'vendor_id = {session["user_id"]}'
    else:
        condition = None
    products = extensions.client.conn.get_rows(TableNames.PRODUCTS.value, condition=condition)
    return len(products)

def _get_complaint_quantity(role: Role) -> int:
    if role == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]} AND complaints.is_accepted = True'
    else:
        condition = f'complaints.is_accepted = True'
    complaints = extensions.client.conn.get_rows(TableNames.PRODUCTS.value,
                                                join_tables=[TableNames.COMPLAINTS.value],
                                                condition=condition)
    return len(complaints)

def _get_monthly_spend() -> dict:
    current_year = datetime.now().year
    keys = [f'{current_year}-{month:02d}' for month in range(1, 13)]
    month_map = {key: 0.00 for key in keys}
    all_orders = extensions.client.customer(session['user_id']).get_orders()
    ytd_orders = [order for order in all_orders if order['order_time'] >= datetime(current_year, 1, 1)]
    for order in ytd_orders:
        order_time = order['order_time']
        if not order_time:
            continue
        month_key = order_time.strftime('%Y-%m')
        order_items = extensions.client.order(order['order_num']).get_order_items()
        if month_key in month_map:
            for item in order_items:
                month_map[month_key] += float(item['qty'])*float(item['unit_price'])
    return {datetime.strptime(key, '%Y-%m').strftime('%b') : round(month_map[key],2) for key in keys}

    

def _get_monthly_revenue(role: Role) -> dict:
    current_year = datetime.now().year
    keys = [f'{current_year}-{month:02d}' for month in range(1, 13)]
    month_map = {key: 0 for key in keys}
    if role == Role.VENDOR:
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
                                          condition=condition,
                                          cols=['orders.order_time','order_items.unit_price','order_items.qty'])

    for row in rows:
        order_time = row.get('order_time')
        if not order_time:
            continue
        month_key = order_time.strftime('%Y-%m')
        if month_key in month_map:
            month_map[month_key] += float(row.get('unit_price')) * float(row.get('qty', 0))

    return {datetime.strptime(key, '%Y-%m').strftime('%b') : month_map[key] for key in keys}

def _get_order_statuses(orders: list[OrderRow]) -> dict:
    status_counts = {'Pending': 0, 'Confirmed': 0, 'Picked Up': 0, 'Shipped': 0}
    for order in orders:
        status = order.get('status')
        if status in status_counts:
            status_counts[status] += 1
    
    total = sum(status_counts.values())
    if total == 0:
        return {key: 0 for key in status_counts}
    
    return {key: value / total for key, value in status_counts.items()}

def _get_order_action(status: str) -> str:
    action = ['Pending', 'Confirmed', 'Picked Up', 'Shipped', ]
    return action[action.index(status)+1] if action.index(status) < 3 else 'Completed'

def _get_orders(role: Role) -> list:
    if role == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]}'
    else:
        condition = None

    orders = extensions.client.conn.get_rows(TableNames.PRODUCTS.value,
                                            join_tables=[TableNames.ORDER_ITEMS.value, TableNames.ORDERS.value, TableNames.USERS.value],
                                            condition=condition,
                                            cols=['DISTINCT order_items.order_num', 'users.name', 'orders.status', 'products.*'])
    return orders

def _get_orders_cost(role: Role) -> dict:
    cost = {}

    if role == Role.VENDOR:
        condition = f'products.vendor_id = {session["user_id"]}'
    else:
        condition = None

    orders = extensions.client.conn.get_rows(TableNames.PRODUCTS.value,
                                            join_tables=[TableNames.ORDER_ITEMS.value, TableNames.ORDERS.value, TableNames.USERS.value],
                                            condition=condition,
                                            cols=['order_items.order_num', 'products.unit_price', 'order_items.qty'])

    for order in orders:
        if order.get('order_num') in cost:
            cost[order.get('order_num')] += order.get('unit_price') * order.get('qty')
        else:
            cost[order.get('order_num')] = order.get('unit_price') * order.get('qty')
    return cost


def get_dashboard_data(role: Role) -> str:
    print(session, role)
    if not check_credentials(role, session.get('user_id')):
        flash('You do not have the necessary credentials', 'error')
        return redirect(url_for('index.index'))

    quick_log = get_quick_log(role)
    graph_log = get_graph_log(role)
    order_log = get_order_log(role)

    return render_template('dash_base.html',
                           role=role.value,
                           quick_log=quick_log,
                           graph_log=graph_log,
                           order_log=order_log)

def get_quick_log(role: Role):
    quick_log = {}
    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        orders = admin.get_all_orders()
        order_items = [extensions.client.order(item['order_num']).get_order_items() for item in orders]
        order_items = [item for sublist in order_items for item in sublist] # unpacks nested list to flat list
        quick_log['revenue'] = _get_revenue(order_items)
        quick_log['products'] = _get_product_quantity(role)
    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        orders = vendor.get_orders()
        order_items = [vendor.order_items_from_order(item['order_num']) for item in orders]
        order_items = [item for sublist in order_items for item in sublist] # unpacks nested list to flat list
        quick_log['revenue'] = _get_revenue(order_items)
        quick_log['products'] = _get_product_quantity(role)
    elif role == Role.CUSTOMER:
        customer = extensions.client.customer(session['user_id'])
        orders = customer.get_orders()
        order_items = [extensions.client.order(item['order_num']).get_order_items() for item in orders]
        order_items = [item for sublist in order_items for item in sublist] # unpacks nested list to flat list
        quick_log['total_spent'] = sum([float(item['unit_price'])*int(item['qty'])
                                        for item in order_items])
        quick_log['cart_items'] = len(customer.get_cart())

    
    quick_log['orders'] = _get_order_quantity(orders)
    quick_log['complaints'] = _get_complaint_quantity(role)

    return quick_log

def get_graph_log(role: Role):
    graph_log = {}
    orders = []
    if role == Role.CUSTOMER:
        graph_log['ytd_spent'] = _get_monthly_spend()
        orders = extensions.client.customer(session['user_id']).get_orders()
    elif role == Role.VENDOR:
        orders = extensions.client.vendor(session['user_id']).get_orders()
    else:
        orders = extensions.client.admin(session['user_id']).get_all_orders()
        graph_log['ytd_rev'] = _get_monthly_revenue(role)
    graph_log['order_status'] = _get_order_statuses(orders)

    return graph_log

def get_order_log(role: Role):
    order_log = {}
    orders = None

    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        orders = admin.get_all_orders()
    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        orders = vendor.get_orders()
    elif role == Role.CUSTOMER:
        customer = extensions.client.customer(session['user_id'])
        orders = customer.get_orders()

    order_log['order_details'] = orders
    order_log['order_costs'] = _get_orders_cost(role)
    order_log['order_actions'] = {order['order_num']: _get_order_action(order.get('status')) for order in orders}

    return order_log

def update_product_status(order_details: dict):
    print('\n\n',order_details['action'],'\n\n')
    extensions.client.conn.update_row(TableNames.ORDERS, pk_value=int(order_details['order_num']), data={'status': order_details['action']})
