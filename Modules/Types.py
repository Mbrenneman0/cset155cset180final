from typing import TypedDict
from datetime import datetime, timedelta
from enum import Enum,auto
import re as Regex

class EditQtyMode(Enum):
    ADDITIVE = auto()
    SET = auto()
    SUBTRACT = auto()

class DiscountType(Enum):
    PERCENTAGE = auto()
    FIXED_AMOUNT = auto()

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
        integers followed by the time unit.\n
        Unit -> Amount\n
        NOT: Amount -> Unit\n
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
        self.time = self._delta_t()

    def _delta_t(self) -> timedelta:
        pattern = r"(\d+)\s*(year|month|week|day)s?"
        matches = Regex.findall(pattern, self.time_str.lower())

        if not matches:
            raise ValueError("Invalid input")

        multipliers = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
        }

        total_days = sum(int(amount) * multipliers[unit] for amount, unit in matches)
        return timedelta(days=total_days)

    def get_end_date(self, start_date:datetime) -> datetime:
        end_date = start_date + self.time
        return end_date
    
    def is_active(self, start_date:datetime) -> bool:
        return datetime.now().date() >= self.get_end_date(start_date).date()
    
class Discount:
    def __init__(self, amount:str, start_date:datetime = None, end_date:datetime= None):
        self.amount = self._parse_discount(amount)
        self.type = self._set_type(amount)
        self.start_date = start_date
        self.end_date = end_date

    def is_active(self) -> bool:
        now = datetime.now()
        if self.start_date is None and self.end_date is None:
            return True
        elif self.start_date is None:
            return now <= self.end_date
        elif self.end_date is None:
            return now >= self.start_date
        return self.start_date <= now <= self.end_date
    
    def _parse_discount(self, amount:str) -> float:
        pattern = r"\d*\.?\d+"
        match = Regex.search(pattern, amount)
        if match:
            return float(match.group())
        else:
            raise ValueError("Invalid discount format")
            
    def _set_type(self, amount:str) -> DiscountType:
        if "%" in amount:
            return DiscountType.PERCENTAGE
        else:
            return DiscountType.FIXED_AMOUNT
        
    def apply_discount(self, price:float) -> float:
        if self.type == DiscountType.PERCENTAGE:
            discount_amount = price * (self.amount / 100)
        else:
            discount_amount = self.amount
        return max(price - discount_amount, 0.0)
    
    def get_discount_amount(self, price:float) -> float:
        if self.type == DiscountType.PERCENTAGE:
            return price * (self.amount / 100)
        else:
            return self.amount



