import extensions
from Modules.Types import *

def send_message(chat_id:int, user_id, content):
    chat = extensions.client.chat(chat_id)
    msg_data = NewChatMessage(chat_id=chat_id,
                        user_id=user_id,
                        content=content)
    chat.conn.create_row(TableNames.MESSAGES, msg_data)

def get_chats(user_id):
    user = extensions.client.user(user_id)
    chats = user.get_chats()
    return chats

def new_chat(user_id, support_id, message:NewChatMessage):
    return