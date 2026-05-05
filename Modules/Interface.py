from . import DBHelper as DBH
from .Types import *

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
            return self.conn.get_rows(TableNames.CHATS, condition=f"customer_id = :user_id OR support_id = :user_id", params={"user_id": self.user_id})

    class Customer(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_cart(self) -> list[CartItem]:
            return self.conn.get_rows(TableNames.CARTS, condition=f"user_id = :user_id", params={"user_id": self.user_id})

        def get_orders(self) -> list[OrderRow]:
            return self.conn.get_rows(TableNames.ORDERS, condition=f"user_id = :user_id", params={"user_id": self.user_id})

        def get_reviews(self):
            return self.conn.get_rows(TableNames.REVIEWS, condition=f"user_id = :user_id", params={"user_id": self.user_id})
        
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

        def create_review(self, sku:str, rating:int, content:str):
            if rating < 1 or rating > 5:
                raise ValueError("rating must be between 1 and 5")
            data = {
                "user_id": self.user_id,
                "sku": sku,
                "rating": rating,
                "content": content
                }
            try:
                self.conn.create_row(TableNames.REVIEWS, data)
            except Exception as e:
                raise

        def create_order(self, items:list[CartItem]):
            order_data = {
                "user_id": self.user_id
            }
            try:
                self.conn.create_row(TableNames.ORDERS, order_data)
                condition="user_id = :user_id ORDER BY order_time DESC LIMIT 1"
                params={"user_id": self.user_id}
                order_num = self.conn.get_rows(TableNames.ORDERS, condition=condition, params=params)[0]["order_num"]
                for item in items:
                    product = self.client.product(item["sku"]).get_info()
                    unit_price = product["unit_price"]
                    warranty_period = product["warranty_period"]
                    item_data = {
                        "order_num": order_num,
                        "sku": item["sku"],
                        "qty": item["qty"],
                        "unit_price": unit_price,
                        "warranty_period": warranty_period
                    }
                    self.conn.create_row(TableNames.ORDER_ITEMS, item_data)
            except Exception as e:
                raise

    class Vendor(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_products(self) -> list[ProductRow]:
            return self.conn.get_rows(TableNames.PRODUCTS, condition=f"vendor_id = :vendor_id", params={"vendor_id": self.user_id})

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
            return self.conn.get_rows(TableNames.REVIEWS, condition=f"products.vendor_id = :user_id", join_tables=["products"], params={"user_id": self.user_id})
        
        def get_orders(self) -> list[OrderRow]:
            rslt = self.conn.get_rows(
                    TableNames.ORDERS,
                    condition="products.vendor_id = :vendor_id",
                    join_tables=[TableNames.ORDER_ITEMS, TableNames.PRODUCTS],
                    cols=[
                        "DISTINCT orders.order_num AS order_num",
                        "orders.user_id AS user_id",
                        "orders.order_time AS order_time",
                        "orders.status AS status"
                    ],
                    params={"vendor_id": self.user_id}
                    )
            orders_list = [OrderRow(order_num=item['order_num'],
                                    user_id=item['user_id'],
                                    order_time=item['order_time'],
                                    status=item['status'])
                                    for item in rslt]
            return orders_list

        def order_items_from_order(self, order_num:int) -> list[OrderItem]:
            order = self.client.order(order_num)
            skus = [item['sku'] for item in self.get_products()]
            order_items = [item for item in order.get_order_items()
                           if item["sku"] in skus]
            return order_items


        def reset_database(self):
            self.conn.reset_db()

    class Admin(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

        def get_all_users(self) -> list[UserRow]:
            return self.conn.get_rows(TableNames.USERS)

        def get_customers(self) -> list[UserRow]:
            return self.conn.get_rows(TableNames.USERS, condition="role = :role", params={"role": Role.CUSTOMER})

        def get_vendors(self):
            return self.conn.get_rows(TableNames.USERS, condition="role = :role", params={"role": Role.VENDOR})

        def get_all_complaints(self) -> list[ComplaintRow]:
            return self.conn.get_rows(TableNames.COMPLAINTS)
        
        def get_unresolved_complaints(self) -> list[ComplaintRow]:
            return self.conn.get_rows(TableNames.COMPLAINTS, condition="is_accepted is NULL")

        def get_all_orders(self) -> list[OrderRow]:
            return self.conn.get_rows(TableNames.ORDERS)

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
            return self.conn.get_rows(TableNames.REVIEWS, condition="sku = :sku", params={"sku": self.sku})

        def get_images(self) -> list[ProductImageRow]:
            return self.conn.get_rows(TableNames.PROD_IMGS, condition="sku = :sku", params={"sku": self.sku})

        def get_discounts(self) -> list[DiscountRow]:
            return self.conn.get_rows(TableNames.DISCOUNTS, condition="sku = :sku", params={"sku": self.sku})

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

    class Order:
        def __init__(self, client: 'Client', order_num):
            self.conn = client.conn
            self.order_num = order_num

        def get_order_items(self) -> list[OrderItem]:
            rslt = self.conn.get_rows(TableNames.ORDERS,
                                      condition= f'{TableNames.ORDERS.value}.order_num = :order_num',
                                      join_tables=['order_items'],
                                      params={'order_num': self.order_num})
            order_items = []
            for item in rslt:
                order_items.append(OrderItem(order_num=self.order_num,
                                             sku=item['sku'],
                                             qty=item['qty'],
                                             unit_price=item['unit_price'],
                                             warranty_period=item['warranty_period']))
            return order_items

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
    
    def order(self, order_id) -> Order:
        return Client.Order(self, order_id)
    
    def message(self, message_id) -> Message:
        return Client.Message(self, message_id)
    
    def chat(self, chat_id) -> Chat:
        return Client.Chat(self, chat_id)
    
    def complaint(self, message_id) -> Complaint:
        return Client.Complaint(self, message_id)
    
    def review(self, message_id) -> Review:
        return Client.Review(self, message_id)
    
    def get_all_products(self) -> list[ProductRow]:
        return self.conn.get_rows(TableNames.PRODUCTS)