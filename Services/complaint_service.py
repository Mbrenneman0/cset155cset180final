import extensions
from Modules.Types import *

def review_complaint(admin_id:int, complaint_id:int, accepted:bool):
    admin = extensions.client.admin(admin_id)
    complaint = admin.client.complaint(complaint_id)
    complaint.set_status(accepted)

def create_complaint(user_id:int, order_num:int, type:ComplaintTypes):
    customer = extensions.client.customer(user_id)
    data = {
        "order_num": order_num,
        "type": type
        }
    customer.conn.create_row(TableNames.COMPLAINTS, data)