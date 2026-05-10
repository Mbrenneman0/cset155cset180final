from flask import flash, session, request, render_template, redirect, url_for
import extensions
from .auth_service import page_gate
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
        condition = f'products.vendor_id = {session["user_id"]}'
    elif role == Role.CUSTOMER:
        condition = f'orders.user_id = {session["user_id"]}'
    else:
        condition = f''
    complaints = extensions.client.conn.get_rows(TableNames.PRODUCTS.value,
                                                join_tables=[TableNames.COMPLAINTS.value, TableNames.ORDERS.value],
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

def get_dashboard_data(role: Role) -> str:
    page_gate(role)

    quick_log = get_quick_log(role)
    graph_log = get_graph_log(role)
    order_log = get_order_log(role)

    return render_template('dash_base.html',
                           role=role.value,
                           quick_log=quick_log,
                           graph_log=graph_log,
                           order_log=order_log,
                           active_page = 'dashboard')

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
        graph_log['ytd_rev'] = _get_monthly_revenue(role)
    else:
        orders = extensions.client.admin(session['user_id']).get_all_orders()
    graph_log['ytd_rev'] = _get_monthly_revenue(role)
    graph_log['order_status'] = _get_order_statuses(orders)

    return graph_log

def get_order_log(role: Role, action:str = None):
    order_log = {}
    orders = None

    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        orders = admin.get_all_orders() if action is None else admin.get_all_orders_filtered(action)
    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        orders = vendor.get_orders() if action is None else vendor.get_orders_filtered(action)
    elif role == Role.CUSTOMER:
        customer = extensions.client.customer(session['user_id'])
        orders = customer.get_orders() if action is None else customer.get_orders_filtered(action)

    order_log['order_details'] = [get_order(order['order_num']) for order in orders]
    order_log['order_actions'] = {order['order_num']: _get_order_action(order.get('status')) for order in orders}

    return order_log

def get_order(order_num:int):
    order = extensions.client.conn.get_row(TableNames.ORDERS, order_num)
    return {'order_num': order['order_num'],
            "name": extensions.client.user(order['user_id']).get_info()['name'],
            "date": order['order_time'],
            "status": order['status'],
            "total": round(sum([float(item['unit_price'])*int(item['qty'])
                                for item in extensions.client.order(order['order_num']).get_order_items()]),2),
            "items": [item for item in extensions.client.order(order['order_num']).get_order_items()]}


def update_product_status(order_details: dict):
    if order_details['action'] != 'Completed':
        extensions.client.conn.update_row(TableNames.ORDERS, pk_value=int(order_details['order_num']), data={'status': order_details['action']})

def get_complaint_data(role: Role):
    page_gate(role)

    complaints = _get_complaints(role)
    customers = [
        extensions.client.conn.get_rows(
            TableNames.USERS,
            condition='orders.order_num = :order_num AND orders.user_id = users.user_id',
            join_tables=[TableNames.ORDERS],
            cols=['name'],
            params={'order_num': complaint['order_num']}
        )[0]
        for complaint in complaints
    ]
    
    if role != 'Customer':
        pending_count = _get_pending_count(role)
        refund_count = _get_refund_count(role)
        resolved_count = _get_resolved_count(role)

        return render_template('dash_complaints.html', role=role,
                                                        complaints=complaints,
                                                        customers=customers,
                                                        pending_count=pending_count,
                                                        refund_count=refund_count,
                                                        resolved_count=resolved_count,
                                                        active_page='complaints')
    
    return render_template('dash_complaints.html', role=role,
                                                    complaints=complaints,
                                                    customers=customers,
                                                    active_page='complaints')

def _get_complaints(role: Role):
    complaints = []
    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        complaints = admin.get_all_complaints()

    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        complaints = vendor.get_product_complaints()

    return complaints

def _get_pending_count(role: Role):
    pending_count = None
    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        pending_count = len(admin.get_unresolved_complaints())

    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        pending_count = len(vendor.get_unresolved_complaints())

    return pending_count

def _get_refund_count(role: Role):
    refund_count = None
    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        refund_count = len(admin.get_complaints_type())

    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        refund_count = len(vendor.get_complaints_type())

    return refund_count

def _get_resolved_count(role: Role):
    resolved_count = None
    if role == Role.ADMIN:
        admin = extensions.client.admin(session['user_id'])
        resolved_count = len(admin.get_all_complaints())-len(admin.get_unresolved_complaints())

    elif role == Role.VENDOR:
        vendor = extensions.client.vendor(session['user_id'])
        resolved_count = len(vendor.get_product_complaints())-len(vendor.get_unresolved_complaints())

    return resolved_count

def update_complaint_status(id: int, status):
    extensions.client.conn.update_row(TableNames.COMPLAINTS,
                                      pk_value=id,
                                      data={'is_accepted': status})