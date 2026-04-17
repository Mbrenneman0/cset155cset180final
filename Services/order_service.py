from extensions import client
from Modules.Types import *

def place_order(user_id: int):
    customer = client.customer(user_id)
        
    #validate order
    cart = customer.get_cart()
    if len(cart) <= 0:
        raise ValueError(f"Cart for user id: {customer.user_id} is empty.")
    for item in cart:
        product = customer.client.product(item["sku"]).get_info()
        if product["qty"] < item["qty"]:
            raise ValueError(f"Available inventory less than cart qty for {item['sku']}")
    
    #create order
    customer.conn.create_row(TableNames.ORDERS, {"user_id": customer.user_id})

    #get order number
    orders = customer.get_orders()
    orders.sort(key=lambda x: x["order_time"])
    new_order = orders.pop()
    order_num = new_order["order_num"]

    #add items from cart to order_items with order number
    for item in cart:
        product = customer.client.product(item["sku"])
        prod_info = product.get_info()
        order_item = OrderItem(order_num= order_num,
                                sku= item["sku"],
                                qty= item["qty"],
                                unit_price=prod_info["unit_price"],
                                warranty_period=prod_info["warranty_period"])
        customer.conn.create_row(TableNames.ORDER_ITEMS, order_item)
        product.update_inventory(item["qty"])

    #clear cart
    customer.clear_cart()