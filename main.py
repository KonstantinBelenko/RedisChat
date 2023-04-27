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

bot = telebot.TeleBot("6123864581:AAFBqwforEzbcav9V-V2LiYwfdilzicdYb4")
chat_app = ChatApp(bot)

# * Add bot hooks here

contacts = ["John", "Mary", "Peter", "Alice"]
main_contact = None
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to my bot!")
    user_id = message.chat.id

@bot.message_handler(commands=['add_contact'])
def add_contact(message):
    if message.text == "/add_contact":
        bot.reply_to(message, "Please write the contact information in the following format: /add_contact <name>")
    else:
        contact_info = message.text.split(maxsplit=1)[1]
        contacts.append(contact_info)
        bot.reply_to(message, f"Contact {contact_info} added successfully.")

@bot.message_handler(commands=['remove_contact'])
def remove_contact(message):
    print(message.text)
    if message.text == "/remove_contact":
        bot.reply_to(message, "Please write the contact information in the following format: /add_contact <name>")
    else:
        contact_name = message.text.split(maxsplit=1)[1]
        if contact_name in contacts:
            contacts.remove(contact_name)
            bot.reply_to(message, f"Contact {contact_name} removed successfully.")
        else:
            bot.reply_to(message, f"Contact {contact_name} not found.")

@bot.message_handler(commands=['switch_contact'])
def switch_contact(message):
    keyboard = types.InlineKeyboardMarkup()
    for contact in contacts:
        callback_button = types.InlineKeyboardButton(text=contact, callback_data=f"switch_contact:{contact}")
        keyboard.add(callback_button)

    bot.send_message(message.chat.id, "Select a contact to switch:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('switch_contact'))
def switch_contact_callback(call):
    contact_name = call.data.split(':')[1]
    global main_contact
    main_contact = contact_name
    bot.answer_callback_query(call.id, text=f"Switched to contact {contact_name}.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if main_contact is None:
        # If there is no main contact, reply with an error message
        bot.reply_to(message, "There is no main contact selected. Please use the /switch_contact command to select a contact.")
    else:
        # Send the message to the main contact
        bot.send_message(main_contact, message.text)

        # Send a confirmation message to the user
        bot.reply_to(message, f"Message sent to {main_contact}.")


# * Add bot hooks here 

def listen_for_messages():
    pubsub = chat_app.redis.pubsub()
    pubsub.subscribe("connected_users")

    for message in pubsub.listen():
        if message["type"] == "message":
            message_data = json.loads(message["data"].decode("utf-8"))
            sender_id = message_data["sender_id"]
            content = message_data["content"]
            chat_id = int(message["channel"].decode("utf-8"))
            bot.send_message(chat_id, f"Message from {sender_id}: {content}")


if __name__ == "__main__":
    import threading

    listen_thread = threading.Thread(target=listen_for_messages)
    listen_thread.setDaemon(True)
    listen_thread.start()

    print("Bot is running...")
    bot.polling()
