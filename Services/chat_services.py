import extensions
from Modules.Types import *

def send_message(chat_id:int, user_id, content):
    chat = extensions.client.chat(chat_id)
    msg_data = NewChatMessage(chat_id=chat_id,
                        user_id=user_id,
                        content=content)
    chat.conn.create_row(TableNames.MESSAGES, msg_data)