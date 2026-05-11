import extensions
from Modules.Types import *

def send_message(message:NewChatMessage):
    msg_data = NewChatMessage(chat_id=message['chat_id'],
                        user_id=message['user_id'],
                        content=message['content'])
    extensions.client.conn.create_row(TableNames.MESSAGES, msg_data)

def get_chats(user_id) -> list[ChatRow]:
    user = extensions.client.user(user_id)
    if user.is_admin():
        user = extensions.client.admin(user_id)
        chats = user.get_complaint_chats()
    else:
        chats = user.get_chats()
    return chats

def create_new_chat(user_id:int, support_id:int, complaint_id:int=None):
    extensions.client.user(user_id).create_chat(support_id, complaint_id)

def get_last_chat(user_id):
    chats = get_chats(user_id)
    chat = max(chats, key=lambda x: x['chat_id'])
    return chat
