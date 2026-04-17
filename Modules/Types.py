from typing import TypedDict
from datetime import datetime, timedelta
from enum import Enum,auto

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