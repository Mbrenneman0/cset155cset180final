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

def get_cart_items():
    user_id = session.get('user_id')
    if not user_id:
        raise Exception("Not logged in")
    else:
        try:
            user = extensions.client.user(user_id)
            if not user.is_customer():
                raise Exception("Only customers can have a cart")
            return extensions.client.customer(user_id).get_cart()
        except Exception as e:
            raise