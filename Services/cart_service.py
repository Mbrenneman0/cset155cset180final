from flask import session
import extensions
from Services.product_service import get_product
from Modules.Types import *

def add_item_to_cart(sku):
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can have a cart")
            extensions.client.customer(user_id).add_to_cart(sku)
        except Exception as e:
            raise

def update_cart_qty(sku, action, qty):
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can have a cart")
            mode = EditQtyMode.SET
            if action == "increase":
                qty = 1
                mode = EditQtyMode.ADDITIVE
            elif action == "decrease":
                qty = 1
                mode = EditQtyMode.SUBTRACT
            elif action == "set":
                mode = EditQtyMode.SET

            if qty <= 0:
                extensions.client.customer(user_id).remove_from_cart(sku)
            else:
                extensions.client.customer(user_id).update_cart_qty(sku, qty, mode)
        except Exception as e:
            raise

def get_cart_items():
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can have a cart")
            cart = extensions.client.customer(user_id).get_cart()
            for item in cart:
                item['product'] = get_product(item['sku'], with_imgs=False, with_discounts=True)
            return cart
        except Exception as e:
            raise

def remove_item_from_cart(sku):
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can have a cart")
            extensions.client.customer(user_id).remove_from_cart(sku)
        except Exception as e:
            raise

def clear_cart():
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can have a cart")
            extensions.client.customer(user_id).clear_cart()
        except Exception as e:
            raise
def checkout():
    # Note: No checkout page. Customer's payment info is assumed to be good according to project specs.
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")

    try:
        user = extensions.client.user(user_id)
        if not user.is_customer():
            raise Exception("Only customers can checkout")
        
        cart_items = extensions.client.customer(user_id).get_cart()
        if not cart_items:
            raise Exception("Your cart is empty")

        order_items = []

        for cart_item in cart_items:
            sku = cart_item["sku"]
            cart_qty = int(cart_item["qty"])

            product = get_product(sku, with_discounts=True)
            stock_qty = int(product["qty"])

            if cart_qty > stock_qty:
                raise Exception(
                    f"Not enough stock for SKU:{sku} {product['title']}. "
                    f"Available: {stock_qty}"
                )
            order_items.append({
                "sku": sku,
                "qty": cart_qty,
                "unit_price": product['sale_price'],
                "warranty_period": product["warranty_period"]
            })

        customer = extensions.client.customer(user_id)
        order_num = customer.create_order(order_items)

        for order_item in order_items:
            extensions.client.product(order_item["sku"]).update_inventory(order_item["qty"])

        clear_cart()
        return order_num

    except Exception:
        raise