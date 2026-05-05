from flask import session
import extensions
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
                item['product'] = extensions.client.product(item['sku']).get_info()
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
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can checkout")
            cart_items = extensions.client.customer(user_id).get_cart()
            if not cart_items:
                raise Exception("Your cart is empty")
            for item in cart_items:
                product = extensions.client.product(item['sku']).get_info()
                if item['qty'] > product['qty']:
                    raise Exception(f"Not enough stock for SKU:{item['sku']} {product['title']}. Available: {product['qty']}")

            extensions.client.customer(user_id).create_order(cart_items)
            clear_cart()
        except Exception as e:
            raise