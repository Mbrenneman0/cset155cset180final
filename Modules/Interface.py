import DBHelper as DBH
from enum import Enum, auto
from typing import TypedDict
from datetime import datetime, timedelta
import re as regex

class EditQtyMode(Enum):
    ADDITIVE = auto()
    SET = auto()
    SUBTRACT = auto()

class TableNames(str, Enum):
    USERS = "users"
    PRODUCTS = "products"
    PROD_IMGS = "prod_imgs"
    DISCOUNTS = "discounts"
    CARTS = "carts"
    ORDERS = "orders"
    ORDER_ITEMS = "order_items"
    REVIEWS = "reviews"
    COMPLAINTS = "complaints"
    CHATS = "chats"
    MESSAGES = "messages"

class Role(str, Enum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    VENDOR = "Vendor"

class ComplaintTypes(str, Enum):
    RETURN = 'Return'
    REFUND ='Refund'
    WARRANTY = 'Warranty'

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
    sku: str
    qty: int
    title: str
    color: str
    size: str
    description: str
    unit_price: float
    warranty_period: str

class ProductImageRow(TypedDict):
    sku: str
    img_url: str

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

class DiscountRow(TypedDict):
    sku: str
    amount: str
    start_date: datetime
    end_date: datetime

class ReviewRow(TypedDict):
    review_id: int
    user_id: int
    sku: str
    rating: int
    content: str
    rvw_time: datetime

class ReviewUpdate(TypedDict, total=False):
    review_id: int
    user_id: int
    sku: str
    rating: int
    content: str
    rvw_time: datetime

class ComplaintRow(TypedDict):
    complaint_id: int
    order_num: int
    content: str
    comp_time: datetime
    type: ComplaintTypes
    is_accepted: bool

class ChatRow(TypedDict, total=False):
    chat_id: int
    complaint_id: int
    customer_id: int
    support_id: int

class ChatMessageRow(TypedDict):
    msg_id: int
    chat_id: int
    user_id: int
    content: str
    msg_time: datetime

class NewChatMessage(TypedDict):
    chat_id: int
    user_id: int
    content: str

class WarrantyPeriod:
    def __init__(self, time:str):
        """
        Time strings must be formated with a series of
        integers followed by the time unit.
        \n
        Examples of valid inputs:\n
        "7 Years, 6 Months and 3 Days"\n
        "7 years 6 months 3 days"\n
        "7year:6month:3day"\n
        \n
        Examples of invalid inputs:\n
        "06/03/07"\n
        "Years: 7, Months: 6, Days: 3"
        """
        self.time_str = time
        self.time = self.delta_t()

    def delta_t(self) -> timedelta:
        substrings = ["year", "month", "week", "day"]
        time = {}
        temp_str = self.time_str
        while True:
            match = regex.search(r"\d+", temp_str)
            if not match:
                break
            temp_int = match.group()
            temp_str = temp_str[match.end():]



class Client:
    def __init__(self, login, password, server, db_name, schema_path):
        self.conn = DBH.Conn(login, password, server, db_name, schema_path)

    class User:
        def __init__(self, client: "Client", user_id):
            self.user_id = user_id
            self.client = client
            self.conn =client.conn
            self.table = TableNames.USERS

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

        def get_chats(self) -> list[ChatRow]:
            return self.conn.get_rows(TableNames.CHATS, f"customer_id = :user_id OR support_id = :user_id", params={"user_id": self.user_id})

    class Customer(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_cart(self) -> list[CartItem]:
            return self.conn.get_rows(TableNames.CARTS, f"user_id = :user_id", params={"user_id": self.user_id})

        def get_orders(self) -> list[OrderRow]:
            return self.conn.get_rows(TableNames.ORDERS, f"user_id = :user_id", params={"user_id": self.user_id})

        def get_reviews(self):
            return self.conn.get_rows(TableNames.REVIEWS, f"user_id = :user_id", params={"user_id": self.user_id})
        
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
                    self.conn.update_row(TableNames.CARTS, (self.user_id, sku), {"qty": new_qty})
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
                self.conn.delete_row(TableNames.CARTS, (self.user_id, sku))

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
            self.conn.create_row(TableNames.ORDERS, {"user_id": self.user_id})

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
                self.conn.create_row(TableNames.ORDER_ITEMS, order_item)
                product.update_inventory(item["qty"])

            #clear cart
            self.clear_cart()

        def create_review(self, sku:str, rating:int, content:str):
            if rating < 1 or rating > 5:
                raise ValueError("rating must be between 1 and 5")
            data = {
                "user_id": self.user_id,
                "sku": sku,
                "rating": rating,
                "content": content
                }
            self.conn.create_row(TableNames.REVIEWS, data)
        
        def create_complaint(self, order_num:int, type:ComplaintTypes):
            data = {
                "order_num": order_num,
                "type": type
                }
            self.conn.create_row(TableNames.COMPLAINTS, data)

    class Vendor(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_products(self) -> list[ProductRow]:
            return self.conn.get_rows(TableNames.PRODUCTS, f"vendor_id = :vendor_id", params={"vendor_id": self.user_id})

        def has_product(self, sku) -> bool:
            products = self.get_products()
            return sku in [row["sku"] for row in products]

        def create_product(self, data:NewProduct):
            params = {"vendor_id": self.user_id}
            params.update(data)
            self.conn.create_row(TableNames.PRODUCTS, params)

        def update_product(self, sku:str, data:ProductUpdate):
            if not self.has_product(sku):
                raise ValueError(f"Vendor: {self.user_id} does not own SKU: {sku}")
            self.client.product(sku).update(data)

        def remove_product(self, sku):
            if not self.has_product(sku):
                raise ValueError(f"Vendor: {self.user_id} does not own SKU: {sku}")
            self.client.product(sku).soft_delete()

        def get_product_reviews(self) -> list[ReviewRow]:
            return self.conn.get_rows(TableNames.REVIEWS, f"products.vendor_id = :user_id", ["products"], {"user_id": self.user_id})

    class Admin(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_all_users(self) -> list[UserRow]:
            return self.conn.get_rows(TableNames.USERS)

        def get_customers(self) -> list[UserRow]:
            return self.conn.get_rows(TableNames.USERS, "role = :role", params={"role": Role.CUSTOMER})

        def get_vendors(self):
            return self.conn.get_rows(TableNames.USERS, "role = :role", params={"role": Role.VENDOR})

        def get_all_complaints(self) -> list[ComplaintRow]:
            return self.conn.get_rows(TableNames.COMPLAINTS)
        
        def get_unresolved_complaints(self) -> list[ComplaintRow]:
            return self.conn.get_rows(TableNames.COMPLAINTS, "is_accepted is NULL")

        def review_complaint(self, complaint_id:int, accepted:bool):
            complaint = self.client.complaint(complaint_id)
            complaint.set_status(accepted)

        def get_all_orders(self) -> list[OrderRow]:
            return self.conn.get_rows(TableNames.ORDERS)

        def get_all_products(self):
            return self.conn.get_rows(TableNames.PRODUCTS)


    class Product:
        def __init__(self, client: "Client", sku):
            self.sku = sku
            self.client = client
            self.conn = client.conn
            self.table = TableNames.PRODUCTS
            if not self.exists():
                raise ValueError(f"SKU {self.sku} does not exist in the database.")

        def exists(self) -> bool:
            rslt = self.conn.get_row(self.table, self.sku)
            return bool(rslt)

        def get_info(self) -> ProductRow:
            rslt = self.conn.get_row(self.table, self.sku)
            return rslt

        def get_reviews(self) -> list[ReviewRow]:
            return self.conn.get_rows(TableNames.REVIEWS, "sku = :sku", params={"sku": self.sku})

        def get_images(self) -> list[ProductImageRow]:
            return self.conn.get_rows(TableNames.PROD_IMGS, "sku = :sku", params={"sku": self.sku})

        def get_discounts(self) -> list[DiscountRow]:
            return self.conn.get_rows(TableNames.DISCOUNTS, "sku = :sku", params={"sku": self.sku})

        def is_available(self) -> bool:
            if self.get_stock() <= 0:
                return False
            if self.get_info()["is_removed"]:
                return False
            return True

        def get_stock(self) -> int:
            return self.get_info()["qty"]

        def update_inventory(self, qty:int, mode:EditQtyMode = EditQtyMode.SUBTRACT):
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
                    self.conn.update_row(self.table, self.sku, {"qty": new_qty})
                except Exception as e:
                    print(e)
                    raise

        def update(self, data:ProductUpdate):
            self.conn.update_row(self.table, self.sku, data)

        def soft_delete(self):
            data = ProductUpdate(is_removed=True)
            self.update(data)

    class Message:
        def __init__(self, client: "Client", message_id):
            self.message_id = message_id
            self.conn =client.conn
            self.table = TableNames.MESSAGES

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
            self.table = TableNames.CHATS

        def get_info(self) -> ChatRow:
            rslt = self.conn.get_row(self.table,self.chat_id)
            return rslt

        def get_messages(self) -> ChatMessageRow:
            return self.conn.get_rows(TableNames.MESSAGES, condition=f'chat_id = :chat_id', params={"chat_id": self.chat_id})

        def send_message(self, user_id, content):
            msg_data = NewChatMessage(chat_id=self.chat_id,
                               user_id=user_id,
                               content=content)
            self.conn.create_row(TableNames.MESSAGES, msg_data)

        def get_participants(self) -> dict:
            rslt = self.conn.get_row(self.table, self.chat_id)
            keep_keys = ['customer_id','support_id']
            return {k: rslt[k] for k in keep_keys if k in rslt}

        def is_complaint(self) -> bool:
            return self.get_info().get('complaint_id') is not None

        def get_complaint(self) -> ComplaintRow:
            if self.is_complaint():
                complaint_id = self.get_info().get('complaint_id')
                rslt = self.conn.get_row(TableNames.COMPLAINTS, complaint_id)
                return rslt
            else:
                raise ValueError (f'The chat at id: {self.chat_id} does not contain a complaint')

    class Complaint(Message):
        def __init__(self, client: "Client", complaint_id):
            super().__init__(client, complaint_id)
            self.complaint_id = complaint_id
            self.table = "complaints"

        def get_info(self) -> ComplaintRow:
            rslt = self.conn.get_row(self.table,self.complaint_id)
            return rslt

        def get_order(self) -> OrderRow:
            order_num = self.get_info().get('order_num')
            rslt = self.conn.get_row('orders', order_num)
            return rslt

        def get_chat(self):
            try:
                rslt = self.conn.get_rows(TableNames.CHATS, condition=f'complaint_id = :complaint_id', params={"complaint_id": self.complaint_id})
                return rslt
            except ValueError:
                raise ValueError (f'The complaint at id: {self.complaint_id} does not have a chat linked to it')

        def set_status(self, is_accepted:bool):
            self.conn.update_row(self.table,self.complaint_id,{'is_accepted':is_accepted})

        def create_chat(self, customer_id:int, support_id:int):
            chat_date = ChatRow(complaint_id=self.complaint_id,
                                customer_id=customer_id,
                                support_id=support_id)
            self.conn.create_row(TableNames.CHATS, chat_date)

    class Review(Message):
        def __init__(self, client: "Client",  review_id):
            super().__init__(client, review_id)
            self.review_id = review_id
            self.table = TableNames.REVIEWS

        def get_info(self) -> ReviewRow:
            rslt = self.conn.get_row(self.table,self.review_id)
            return rslt

        def update(self, data:ReviewUpdate):
            self.conn.update_row(self.table, self.review_id, data)

        def delete(self):
            self.conn.delete_row(self.table, self.review_id)

        def get_author(self):
            user_id = self.get_info().get('user_id')
            rslt = self.conn.get_row(TableNames.USERS, user_id)
            return rslt

        def get_product(self):
            sku = self.get_info().get('sku')
            rslt = self.conn.get_row(TableNames.PRODUCTS, sku)
            return rslt

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