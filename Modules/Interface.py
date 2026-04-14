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
            if mode != EditQtyMode.SET:
                current_qty = self.get_cart_qty(sku)
            if qty < 0:
                raise ValueError("qty must be greater than 0")
            if mode == EditQtyMode.SUBTRACT:
                if
            in_cart = self.is_in_cart(sku)
            if not in_cart:
                self.add_to_cart(sku, qty)
            else:
                

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

        def get_content(self):

        def delete(self):

    class Chat:
        def __init__(self, client: "Client", chat_id):
            self.chat_id = chat_id
            self.conn = client.conn
            self.table = "chats"

        def get_info(self):

        def get_messages(self):

        def send_message(self, user_id, content):

        def get_participants(self):

        def is_complaint(self) -> bool:

        def get_complaint(self):


    class Complaint(Message):
        def __init__(self, client: "Client", complaint_id):
            super().__init__(client, complaint_id)
            self.table = "complaints"

        def get_info(self):

        def get_order(self):

        def get_chat(self):

        def set_status(self, is_accepted):

        def create_chat(self, customer_id, support_id):


    class Review(Message):
        def __init__(self, client: "Client",  review_id):
            super().__init__(client, review_id)
            self.table = "reviews"

        def get_info(self):

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