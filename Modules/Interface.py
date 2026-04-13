import DBHelper as DBH

class Client:
    def __init__(self, login, password, server, db_name, schema_path):
        self.conn = DBH.Conn(login, password, server, db_name, schema_path)

    class Entity:

    class User(Entity):

    class Customer(User):

    class Vendor(User):

    class Admin(User):

    class Product(Entity):

    class Message(Entity):

    class Chat(Message):

    class Complaint(Message):

    class Review(Message):