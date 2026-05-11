from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from Modules.Types import Role
from Services.dash_service import get_dashboard_data, update_product_status, get_order_log, get_order, get_complaint_data, update_complaint_status
from Services.product_service import get_products, get_product, update_product, new_sku, add_new_product
from Services.chat_services import *
from Services.auth_service import role_required

dash_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dash_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))
    role = session.get('role')
    if role in [Role.VENDOR.value, Role.ADMIN.value, Role.CUSTOMER.value]:
        return redirect(url_for(f'dashboard.{role.lower()}_dash'))
    else:
        flash('Invalid user role. Please log in again.')
        return redirect(url_for('index.index'))

# ------------ MAIN DASH ----------------
@dash_bp.route('/vendor', methods=['GET','POST'])
@role_required(Role.VENDOR)
def vendor_dash():
    if request.method == 'POST':
        update_product_status(dict(request.form))
    return get_dashboard_data(Role.VENDOR)

@dash_bp.route('/admin', methods=['GET','POST'])
@role_required(Role.ADMIN)
def admin_dash():
    if request.method == 'POST':
        update_product_status(dict(request.form))
    return get_dashboard_data(Role.ADMIN)

@dash_bp.route('/account')
@role_required(Role.CUSTOMER)
def customer_dash():
    return get_dashboard_data(Role.CUSTOMER)

@dash_bp.route('/<string:role>/account-info')
def account_info(role):
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))

    user_id = session['user_id']
    role_lower = role.lower()

    if role_lower == Role.CUSTOMER.value.lower():
        account = extensions.client.customer(user_id).get_info()
    elif role_lower == Role.VENDOR.value.lower():
        account = extensions.client.vendor(user_id).get_info()
    elif role_lower == Role.ADMIN.value.lower():
        account = extensions.client.admin(user_id).get_info()
    else:
        flash('Invalid dashboard role.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    account.pop('password', None)

    return render_template(
        'dash_acct_info.html',
        role=role,
        account=account,
        active_page='info'
    )

# ----- PRODUCTS ------
@dash_bp.route('/<role>/products')
@role_required(Role.VENDOR, Role.ADMIN)
def view_products(role):
    products = get_products(with_imgs=True)
    if role == Role.VENDOR.value:
        products = [product for product in products if product['vendor_id'] == session['user_id']]
    return render_template('dash_products.html', products= products, role= role, active_page = 'products')


@dash_bp.route('/<string:role>/products/<string:sku>/edit', methods=['GET', 'POST'])
@role_required(Role.VENDOR, Role.ADMIN)
def edit_product(role, sku):
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))

    product = get_product(sku, with_imgs=True)

    if role == Role.VENDOR.value and product['vendor_id'] != session['user_id']:
        flash("You cannot edit another vendor's product.", "error")
        return redirect(url_for('dashboard.view_products', role=role))

    if request.method == 'POST':
        update_product(
            request.form,
            new_images=request.files.getlist('images'),
            delete_images=request.form.getlist('delete_images')
        )
        flash('Product updated successfully.', 'info')
        return redirect(url_for('dashboard.view_products', role=role))
    
    return render_template(
        'dash_edit_product.html',
        role=role,
        product=product,
        categories=ProdCategories,
        active_page = 'products'
        )

@dash_bp.route('/<string:role>/products/new', methods=['GET', 'POST'])
def add_product(role):
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))

    sku = new_sku()
    user_id = session['user_id']
    vendor_ids = [user['user_id'] for user in extensions.client.admin(1).get_vendors()]

    if request.method == 'POST':
        add_new_product(
            request.form,
            image=request.files.getlist('images')[0]
        )
        flash('Product added successfully.', 'info')
        return redirect(url_for('dashboard.view_products', role=role))

    return render_template(
        'dash_add_product.html',
        user_id=user_id,
        vendors = vendor_ids,
        categories = ProdCategories,
        sku=sku,
        role=role,
        active_page='products'
    )

# ----- CHATS -------

@dash_bp.route('/<string:role>/chats')
def view_chats(role):
    chats = get_chats(session['user_id'])
    for chat in chats:
        chat['customer'] = extensions.client.user(chat['customer_id']).get_info()['name']
        chat['support'] = extensions.client.user(chat['support_id']).get_info()['username']
    return render_template('dash_chats.html', chats=chats, role=role, active_page="messages")

@dash_bp.route('/<string:role>/chats/<int:chat_id>', methods=['GET', 'POST'])
def view_chat(role, chat_id):
    if 'user_id' not in session:
        return redirect(url_for('authenticate.login_username'))

    chat_obj = extensions.client.chat(chat_id)
    chat = chat_obj.get_info()

    current_user_id = session['user_id']
    current_role = session.get('role')

    is_participant = current_user_id in [
        chat['customer_id'],
        chat['support_id']
    ]

    if current_role != Role.ADMIN.value and not is_participant:
        flash("You do not have permission to view this chat.", "error")
        return redirect(url_for('dashboard.view_chats', role=role))

    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if content:
            send_message({
                'chat_id': chat_id,
                'user_id': current_user_id,
                'content': content
            })

        return redirect(url_for(
            'dashboard.view_chat',
            role=role,
            chat_id=chat_id
        ))

    messages = chat_obj.get_messages()

    customer = extensions.client.user(chat['customer_id']).get_info()

    support = None
    if chat.get('support_id'):
        support = extensions.client.user(chat['support_id']).get_info()

    chat['customer_name'] = customer['name']
    chat['support_username'] = support['username'] if support else 'Not assigned'

    user_display_names = {
        chat['customer_id']: customer['name']
    }

    if support:
        user_display_names[chat['support_id']] = support['name']

    for message in messages:
        message['author'] = user_display_names.get(
            message['user_id'],
            f"User #{message['user_id']}"
        )

    return render_template(
        'dash_view_chat.html',
        chat=chat,
        messages=messages,
        role=role,
        active_page='messages'
    )
    
@dash_bp.route('<string:role>/chats/new', methods=["GET", "POST"])
def new_chat(role:Role):
    if request.method == "GET":
        vendors = [{'user_id': user['user_id'], 'name':user['name']}
                   for user in extensions.client.admin(1).get_vendors()]
        return render_template('dash_new_chat.html',
                               vendors=vendors,
                               role=session.get('role')
        )
    if request.method == "POST":
        form = request.form
        user_id = session['user_id']
        support_id = form.get('vendor_id')
        create_new_chat(user_id, support_id)
        chat_id = get_last_chat(user_id)['chat_id']
        message = NewChatMessage(chat_id=chat_id,
                                 user_id=user_id,
                                 content=form.get('message'))
        send_message(message)
        return redirect(url_for('dashboard.view_chat', role=role, chat_id=chat_id))

    
# ----- ORDERS -------
@dash_bp.route('/<role>/orders', methods=['GET','POST'])
def view_orders(role):
    if request.method == 'POST':
        if request.form.get('bulk_action'):
            orders = request.form.getlist('orders')
            STATUS_FLOW = {
                'Pending': 'Confirmed',
                'Confirmed': 'Picked Up',
                'Picked Up': 'Shipped'
            }
            for order_num in orders:
                order = get_order(order_num)
                order['action'] = STATUS_FLOW.get(order['status'])
                if order['action']:
                    update_product_status(order) 
        else:
            update_product_status(request.form)
    return render_template('dash_orders.html', role=role, 
                                                order_log=get_order_log(session['role']),
                                                active_page='orders')

@dash_bp.route('/<role>/orders/<action>', methods=['GET','POST'])
def view_filtered_orders(role, action):
    if request.method == 'POST':
        if request.form.get('bulk_action'):
            orders = request.form.getlist('orders')
            STATUS_FLOW = {
                'Pending': 'Confirmed',
                'Confirmed': 'Picked Up',
                'Picked Up': 'Shipped'
            }
            for order_num in orders:
                order = get_order(order_num)
                order['action'] = STATUS_FLOW.get(order['status'])
                if order['action']:
                    update_product_status(order)  
        else:
            update_product_status(request.form)
    return render_template('dash_orders.html', role=role, 
                                                order_log=get_order_log(session['role'], action), 
                                                action=action, 
                                                active_page='orders')

# ------ COMPLAINTS --------
@dash_bp.route('/<role>/complaints', methods=['GET','POST'])
def view_complaints(role):
    if request.method == 'POST':
        return
    return get_complaint_data(role)
@dash_bp.post("/<role>/complaints/<int:cid>/accept")
def accept_comp(cid, role):
    update_complaint_status(cid, True)
    return redirect(f"/dashboard/{role}/complaints")

@dash_bp.post("/<role>/complaints/<int:cid>/reject")
def reject_comp(cid, role):
    update_complaint_status(cid, False)
    return redirect(f"/dashboard/{role}/complaints")

@dash_bp.route("/<role>/complaints/new", methods=["GET", "POST"])
def create_complaint(role):
    if request.method == "POST":
        form = request.form
        user_id = session['user_id']
        
        customer = extensions.client.customer(user_id)
        customer.create_complaint(form['order_num'], form['sku'], form['content'], form['type'])

        complaint_id = customer.get_all_complaints()[0]['complaint_id']
        #---- after complaint object is generated, get the complaint_id and store it in variable named complaint_id
        message = form.get('content')
        support_id = 1 #admin_id
        create_new_chat(user_id, support_id, complaint_id=complaint_id)
        chat_id = get_last_chat(user_id)['chat_id']
        message = NewChatMessage(chat_id=chat_id,
                                 user_id=user_id,
                                 content=message)
        send_message(message)

        if form['submit_type'] == 'Submit Complaint':
            return redirect(url_for(
                'dashboard.view_orders',
                role=role
            ))

        else:
            return redirect(url_for(
                'dashboard.view_chat',
                role=role,
                chat_id=chat_id
            ))