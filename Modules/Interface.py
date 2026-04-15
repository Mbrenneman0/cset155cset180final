import DBHelper as DBH
from enum import Enum, auto
from typing import TypedDict
from datetime import datetime

class EditQtyMode(Enum):
    ADDITIVE = auto()
    SET = auto()
    SUBTRACT = auto()

class Role(str, Enum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    VENDOR = "Vendor"

class UserRow(TypedDict):
    user_id: int
    name: str
    username: str
    password: str
    email: str
    role: Role

class UserUpdate(TypedDict, total=False):
    name: str
    username: str
    password: str
    email: str
    role: Role

class CartItem(TypedDict):
    user_id: int
    sku: str
    qty: int

class OrderRow(TypedDict):
    order_num: int
    user_id: int
    order_time: datetime
    status: str

class OrderItem(TypedDict):
    order_num: int
    sku: str
    qty: int
    unit_price: float
    warranty_period: str

class ProductRow(TypedDict):
    sku: str
    vendor_id: int
    qty: int
    title: str
    color: str
    size: str
    description: str
    unit_price: float
    warranty_period: str
    is_removed: bool

class NewProduct(TypedDict):
    sku:str
    qty:int
    title:str
    color:str
    size:str
    description: str
    unit_price:float
    warranty_period:str

class ProductUpdate(TypedDict, total=False):
        sku: str
        qty: int
        title: str
        color: str
        size: str
        description: str
        unit_price: float
        warranty_period: str
        is_removed: bool

#possible warranty period class? to parse warranty_period strings and calculate dates

class Review(TypedDict):
    review_id: int
    user_id: int
    sku: str
    rating: int
    content: str
    rvw_time: datetime

class Complaint(TypedDict):
    complaint_id: int
    order_num: int
    comp_time: datetime
    type: str
    is_accepted: bool

class Chat(TypedDict, total=False):
    chat_id: int
    complaint_id: int
    customer_id: int
    support_id: int

class Message(TypedDict):
    msg_id: int
    chat_id: int
    user_id: int
    content: str
    msg_time: datetime


class Client:
    def __init__(self, login, password, server, db_name, schema_path):
        self.conn = DBH.Conn(login, password, server, db_name, schema_path)

    class User:
        def __init__(self, client: "Client", user_id):
            self.user_id = user_id
            self.client = client
            self.conn =client.conn
            self.table = "users"

        def get_info(self) -> UserRow:
            rslt = self.conn.get_row(self.table, self.user_id)
            return rslt

        def get_role(self) -> str:
            rslt = self.get_info()
            return rslt.get("role")
        
        def is_customer(self) -> bool:
            return self.get_role() == Role.CUSTOMER
        
        def is_vendor(self) -> bool:
            return self.get_role() == Role.VENDOR
        
        def is_admin(self) -> bool:
            return self.get_role() == Role.ADMIN
        
        def update_profile(self, data:UserUpdate):
            self.conn.update_row(self.table, self.user_id, data)

        def get_chats(self) -> list[Chat]:
            return self.conn.get_rows("chats", f"customer_id = {self.user_id} OR support_id = {self.user_id}")

    class Customer(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_cart(self) -> list[CartItem]:
            return self.conn.get_rows("carts", f"user_id = {self.user_id}")

        def get_orders(self) -> list[OrderRow]:
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
            in_cart = self.is_in_cart(sku)
            if in_cart:
                self.update_cart_qty(sku, qty, EditQtyMode.ADDITIVE)
            else:
                data = {
                    "user_id": self.user_id,
                    "sku": sku,
                    "qty": qty
                }
                self.conn.create_row("carts", data)

        def remove_from_cart(self, sku):
            in_cart = self.is_in_cart(sku)
            if not in_cart:
                raise ValueError(f"SKU: {sku} not found in database.")
            else:
                self.conn.delete_row("carts", (self.user_id, sku))

        def clear_cart(self):
            cart = [row["sku"] for row in self.get_cart()]
            for sku in cart:
                self.remove_from_cart(sku)

        def place_order(self):
            
            #validate order
            cart = self.get_cart()
            if len(cart) <= 0:
                raise ValueError(f"Cart for user id: {self.user_id} is empty.")
            for item in cart:
                product = self.client.product(item["sku"]).get_info()
                if product["qty"] < item["qty"]:
                    raise ValueError(f"Available inventory less than cart qty for {item['sku']}")
            
            #create order
            self.conn.create_row("orders", {"user_id": self.user_id})

            #get order number
            orders = self.get_orders()
            orders.sort(key=lambda x: x["order_time"])
            new_order = orders.pop()
            order_num = new_order["order_num"]

            #add items from cart to order_items with order number
            for item in cart:
                product = self.client.product(item["sku"])
                prod_info = product.get_info()
                order_item = OrderItem(order_num= order_num,
                                       sku= item["sku"],
                                       qty= item["qty"],
                                       unit_price=prod_info["unit_price"],
                                       warranty_period=prod_info["warranty_period"])
                self.conn.create_row("order_items", order_item)
                product.update_inventory(item["qty"])

            #clear cart
            self.clear_cart()

        def create_review(self, sku:str, rating:int, content:str):
            if rating < 1 or rating > 5:
                raise ValueError("rating must be between 0 and 5")
            data = {
                "user_id": self.user_id,
                "sku": sku,
                "rating": rating,
                "content": content
                }
            self.conn.create_row("reviews", data)
        
        def create_complaint(self, order_num:int, type:str):
            data = {
                order_num: int,
                type: str
                }
            self.conn.create_row("complaints", data)

    class Vendor(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_products(self) -> list[ProductRow]:
            return self.conn.get_rows("products", f"vendor_id = {self.user_id}")

        def has_product(self, sku) -> bool:
            products = self.get_products()
            return sku in [row["sku"] for row in products]

        def create_product(self, data:NewProduct):
            params = {"vendor_id": self.user_id}
            params.update(data)
            self.conn.create_row("products", params)

        def update_product(self, sku:str, data:ProductUpdate):
            if not self.has_product(sku):
                raise ValueError(f"Vendor: {self.user_id} does not own SKU: {sku}")
            self.conn.update_row("products", sku, data)

        def remove_product(self, sku):
            if not self.has_product(sku):
                raise ValueError(f"Vendor: {self.user_id} does not own SKU: {sku}")
            data = ProductUpdate(is_removed=True)
            self.update_product(sku, data)

        def get_product_reviews(self) -> list[Review]:
            return self.conn.get_rows("reviews", f"products.vendor_id = :user_id", ["products"], {"user_id": self.user_id})

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
            self.client = client
            self.conn = client.conn
            self.table = "products"

        def exists(self) -> bool:
            rslt = self.conn.get_row("products", self.sku)
            return bool(rslt)

        def get_info(self) -> ProductRow:
            rslt = self.conn.get_row("products", self.sku)
            return rslt

        def get_reviews(self):

        def get_images(self):

        def get_discounts(self):

        def is_available(self):
        # Check qty > 0 and maybe is_removed == FALSE

        def get_stock(self) -> int:
            return self.get_info()["qty"]

        def update_inventory(self, qty, mode:EditQtyMode = EditQtyMode.SUBTRACT):
            exists = self.exists()
            if not exists:
                raise ValueError(f"SKU {self.sku} does not exist in the database.")
            else:
                current_qty = self.get_stock()
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
                else:
                    try:
                        self.conn.update_row("products", self.sku, {"qty": new_qty})
                    except Exception as e:
                        print(e)
                        raise


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
                rslt = self.conn.get_rows('chats', condition=f'complaint_id = {self.complaint_id}')
                return rslt
            except ValueError:
                raise ValueError (f'The complaint at id: {self.complaint_id} does not have a chat linked to it')

        def set_status(self, is_accepted):
            self.conn.update_row(self.table,self.complaint_id,{'is_accepted':is_accepted})

        def create_chat(self, customer_id, support_id):
            chat_date = {'complaint_id':self.complaint_id,
                         'customer_id': customer_id,
                         'support_id': support_id}
            self.conn.create_row('chats', chat_date)

    class Review(Message):
        def __init__(self, client: "Client",  review_id):
            super().__init__(client, review_id)
            self.review_id = self.review_id
            self.table = "reviews"

        def get_info(self):
            rslt = self.conn.get_row(self.table,self.review_id)
            return rslt

        def update(self, data):
            self.conn.update_row(self.review_id, data)

        def delete(self):
            self.conn.delete_row(self.table, self.review_id)

        def get_author(self):
            user_id = self.get_info().get('user_id')
            rslt = self.conn.get_rows('users',condition=f'user_id = {user_id}')
            return rslt

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