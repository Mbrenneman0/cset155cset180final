import DBHelper as DBH

class Client:
    def __init__(self, login, password, server, db_name, schema_path):
        self.conn = DBH.Conn(login, password, server, db_name, schema_path)

    class User:
        def __init__(self, client: "Client", user_id):
            self.user_id = user_id
            self.conn =client.conn
            self.table = "users"

        def get_role(self) -> str:
            rslt = self.conn.get_row(self.table, self.user_id)
            return rslt.get("role")

    class Customer(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

    class Vendor(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

    class Admin(User):
        def __init__(self, client: "Client", user_id):
            super().__init__(client, user_id)

    class Product:
        def __init__(self, client: "Client", sku):
            self.sku = sku
            self.conn =client.conn
            self.table = "products"

    class Message:
        def __init__(self, client: "Client", message_id):
            self.message_id = message_id
            self.conn =client.conn
            self.table = "messages"

    class Chat(Message):
        def __init__(self, client: "Client", message_id):
            super().__init__(client, message_id)

    class Complaint(Message):
        def __init__(self, client: "Client", complaint_id):
            super().__init__(client, complaint_id)
            self.table = "complaints"

    class Review(Message):
        def __init__(self, client: "Client",  review_id):
            super().__init__(client, review_id)
            self.table = "reviews"

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