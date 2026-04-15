import DBHelper as DBH
from enum import Enum, auto

class EditQtyMode(Enum):
    ADDITIVE = auto()
    SET = auto()
    SUBTRACT = auto()

class Client:
    def __init__(self, login, password, server, db_name, schema_path):
        self.conn = DBH.Conn(login, password, server, db_name, schema_path)

    class User:
        def __init__(self, client: "Client", user_id):
            self.user_id = user_id
            self.conn =client.conn
            self.table = "users"

        def get_info(self):
            rslt = self.conn.get_row(self.table, self.user_id)

        def get_role(self) -> str:
            rslt = self.conn.get_row(self.table, self.user_id)
            return rslt.get("role")
        
        def is_customer(self) -> bool:
            return self.get_role() == "Customer"
        
        def is_vendor(self) -> bool:
            return self.get_role() == "Vendor"
        
        def is_admin(self) -> bool:
            return self.get_role() == "Admin"
        
        def update_profile(self, data:dict):
            self.conn.update_row(self.table, self.user_id, data)

    class Customer(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_cart(self):
            return self.conn.get_rows("carts", f"user_id = {self.user_id}")

        def get_orders(self):
            return self.conn.get_rows("orders", f"user_id = {self.user_id}")

        def get_reviews(self):
            return self.conn.get_rows("reviews", f"user_id = {self.user_id}")
        
        def is_in_cart(self, sku:str) -> bool:
            return sku in [item["sku"] for item in self.get_cart()]
        
        def get_cart_qty(self, sku:str) -> int:
            cart = self.get_cart()
            for item in cart:
                if item["sku"] == sku:
                    return item["qty"]
            return 0
        
        def update_cart_qty(self, sku, qty:int=1, mode:EditQtyMode = EditQtyMode.SET):
            in_cart = self.is_in_cart(sku)
            if not in_cart:
                current_qty = 0
            else:
                current_qty = self.get_cart_qty(sku)
            
            if mode == EditQtyMode.ADDITIVE:
                new_qty = current_qty + qty
            elif mode == EditQtyMode.SUBTRACT:
                new_qty = current_qty - qty
            elif mode == EditQtyMode.SET:
                new_qty = qty
            else:
                raise TypeError("mode must use the Enum EditQtyMode")
            if new_qty < 0:
                raise ValueError("New qty must be greater than or equal to 0")
            elif new_qty == 0:
                self.remove_from_cart(sku)
            elif not in_cart:
                self.add_to_cart(sku, new_qty)
            else:
                try:
                    self.conn.update_row("carts", (self.user_id, sku), {"qty": new_qty})
                except Exception as e:
                    print(e)
                    raise

        def add_to_cart(self, sku, qty:int=1):

        def remove_from_cart(self, sku):

        def clear_cart(self):

        def place_order(self):

        def create_review(self, sku, rating, content):
        
        def create_complaint(self, order_num, type):

        def get_chats(self):

    class Vendor(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_products(self):

        def get_product(self, sku):

        def create_product(self, data):

        def update_product(self, sku, data):

        def remove_product(self, sku):
            #set is_removed to true, dont actually remove from db

        def get_product_reviews(self):

    class Admin(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_all_users(self):

        def get_customers(self):

        def get_vendors(self):

        def get_all_complaints(self):

        def review_complaint(self, complaint_id, accepted):

        def get_all_orders(self):

        def get_all_products(self):


    class Product:
        def __init__(self, client: "Client", sku):
            self.sku = sku
            self.conn =client.conn
            self.table = "products"

        def get_info(self):

        def get_reviews(self):

        def get_images(self):

        def get_discounts(self):

        def is_available(self):
        # Check qty > 0 and maybe is_removed == FALSE

        def update(self, data):
        # Vendor/admin useself.

        def soft_delete(self):

    class Message:
        def __init__(self, client: "Client", message_id):
            self.message_id = message_id
            self.conn =client.conn
            self.table = "messages"

        def get_info(self):
            rslt = self.conn.get_row(self.table,self.message_id)
            return rslt

        def get_content(self):
            return self.get_info().get('content')

        def delete(self):
            self.conn.delete_row(self.table,self.message_id)

    class Chat:
        def __init__(self, client: "Client", chat_id):
            self.chat_id = chat_id
            self.conn = client.conn
            self.table = "chats"

        def get_info(self):
            rslt = self.conn.get_row(self.table,self.chat_id)
            return rslt

        def get_messages(self):
            return self.conn.get_rows('messages', condition=f'chat_id = {self.chat_id}')

        def send_message(self, user_id, content):

            return 

        def get_participants(self) -> dict:
            rslt = self.conn.get_row(self.table, self.chat_id)
            keep_keys = ['customer_id','support_id']
            return {k: rslt[k] for k in keep_keys if k in rslt}

        def is_complaint(self) -> bool:
            rslt = self.get_info()
            if rslt.get('complaint_id') is None:
                return False
            else:
                return True

        def get_complaint(self):
            if self.is_complaint():
                complaint_id = self.get_info.get('complaint_id')
                rslt = self.conn.get_rows('complaints',condition=f'complaint_id = {complaint_id}')
                return rslt
            else:
                raise ValueError (f'The chat at id: {self.chat_id} does not contain a complaint')

    class Complaint(Message):
        def __init__(self, client: "Client", complaint_id):
            super().__init__(client, complaint_id)
            self.complaint_id = self.complaint_id
            self.table = "complaints"

        def get_info(self):
            rslt = self.conn.get_row(self.table,self.complaint_id)
            return rslt

        def get_order(self):
            order_num = self.get_info().get('order_num')
            rslt = self.conn.get_rows('orders', condition=f'order_num = {order_num}')
            return rslt

        def get_chat(self):
            try:
                rslt = self.conn.get
            except ValueError:
                raise ValueError ('This complaint does not have a chat linked to it')

        def set_status(self, is_accepted):

        def create_chat(self, customer_id, support_id):


    class Review(Message):
        def __init__(self, client: "Client",  review_id):
            super().__init__(client, review_id)
            self.review_id = self.review_id
            self.table = "reviews"

        def get_info(self):
            rslt = self.conn.get_row(self.table,self.review_id)
            return rslt

        def update(data):

        def delete(self):

        def get_author(self):

        def get_product(self):

    def user(self, user_id) -> User:
        return Client.User(self, user_id)
            
    def customer(self, user_id) -> Customer:
        return Client.Customer(self, user_id)
    
    def vendor(self, user_id) -> Vendor:
        return Client.Vendor(self, user_id)
    
    def admin(self, user_id) -> Admin:
        return Client.Admin(self, user_id)
    
    def product(self, sku) -> Product:
        return Client.Product(self, sku)
    
    def message(self, message_id) -> Message:
        return Client.Message(self, message_id)
    
    def chat(self, message_id) -> Chat:
        return Client.Chat(self, message_id)
    
    def complaint(self, message_id) -> Complaint:
        return Client.Complaint(self, message_id)
    
    def review(self, message_id) -> Review:
        return Client.Review(self, message_id)