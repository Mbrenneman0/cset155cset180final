import extensions
from Modules.Types import *

def acct_route(user_id):
    try:
        user = extensions.client.user(user_id)
        if user.is_admin():
            return 'dashboard.admin_dash'
        elif user.is_vendor():
            return 'dashboard.vendor_dash'
        elif user.is_customer():
            return 'index.index' # replace with customer dashboard when created
        else:
            raise Exception("User has no account type")
    except Exception as e:
        raise