import telebot
import redis
import json
import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")

class ChatApp:
    def __init__(self, bot):
        self.bot = bot
        self.redis = redis.Redis()

    def _user_contacts_key(self, user_id):
        return f"contacts:{user_id}"

    def add_contact(self, user_id, contact_id):
        self.redis.sadd(self._user_contacts_key(user_id), contact_id)

    def remove_contact(self, user_id, contact_id):
        self.redis.srem(self._user_contacts_key(user_id), contact_id)

    def is_contact(self, user_id, contact_id):
        return self.redis.sismember(self._user_contacts_key(user_id), contact_id)

    def send_message(self, sender_id, receiver_id, content):
        if self.is_contact(sender_id, receiver_id):
            message_data = {"sender_id": sender_id, "content": content}
            self.redis.publish(receiver_id, json.dumps(message_data))
        else:
            print(f"{receiver_id} is not in your contacts.")

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
chat_app = ChatApp(bot)