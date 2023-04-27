import json
import os
from redis_messenger import RedisMessenger

def check_user_config(config_path: str = "./user_config.json"):

    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            return config
        
    else:
        return False

def save_user_config(user_id, messenger):
    contacts = messenger.list_contacts(user_id)
    config = {
        'user_id': user_id,
        'contacts': [contact['user_id'] for contact in contacts]
    }
    with open('user_config.json', 'w') as config_file:
        json.dump(config, config_file)
    print("User configuration saved to user_config.json")

def mark_messages_seen(messenger, message_keys):
    for message_key in message_keys:
        messenger.redis_conn.hset(message_key, 'seen', True)

def print_unseen_messages(messenger, user_id):
    unseen_count = 0
    unseen_messages = {}
    message_keys = messenger.redis_conn.zrange(f'user_messages:{user_id}', 0, -1)
    for message_key in message_keys:
        message_data_raw = messenger.redis_conn.hgetall(message_key)
        message_data = {k.decode(): v.decode() for k, v in message_data_raw.items()}
        if message_data.get('seen') == 'False':
            unseen_count += 1
            unseen_messages[message_data['sender_id']] = unseen_messages.get(message_data['sender_id'], 0) + 1

    if unseen_count > 0:
        print(f"\nYou have {unseen_count} unseen messages:")
        for sender_id, count in unseen_messages.items():
            sender_data = messenger.redis_conn.hgetall(f"user:{sender_id}")
            sender_username = sender_data[b'username'].decode()
            print(f"- {count} messages from {sender_username}")
        print()

def main():
    messenger = RedisMessenger()

    config = check_user_config()
    if not config:

        print("Welcome to Redis Chat!")
        print("Enter your user ID or type 'new' to create a new user:")
        user_input = input()

        if user_input == 'new':
            print("Enter a username:")
            username = input()
            try:
                user_id = messenger.create_user(username)
                print(f"User created! Your user ID is: {user_id}")
            except ValueError as e:
                print(e)
                return
        else:
            user_id = user_input

    else:
        user_id = config['user_id']
        
    while True:
        print_unseen_messages(messenger, user_id)
        print("\nOptions:")
        print("1. List users in your contact list")
        print("2. Send message to a user by their username")
        print("3. Add user to your contact list by their UUID")
        print("4. List last 10 messages from a user")
        print("5. Save configuration")
        print("6. Exit")
        option = input("Choose an option: ")

        if option == '1':
            if option == '1':
                # List users in your contact list
                print("Your contact list:")
                contacts = messenger.list_contacts(user_id)
                for contact in contacts:
                    print(f"{contact['username']} (ID: {contact['user_id']})")
        elif option == '2':
            # Send message to a user by their username
            print("Enter the username of the user you want to send a message to:")
            contact_username = input()
            contact_id = messenger.redis_conn.hget('usernames', contact_username)
            
            if contact_id:
                print("Enter your message:")
                message = input()
                message_id = messenger.send_message(user_id, contact_id.decode(), message)
                print(f"Message sent with ID: {message_id}")
            else:
                print("Invalid username. No user found with the given username.")
        elif option == '3':
            # Add user to your contact list by their UUID
            print("Enter the UUID of the user you want to add to your contact list:")
            contact_id = input()
            
            # Check if the entered contact_id exists
            if messenger.redis_conn.exists(f'user:{contact_id}'):
                messenger.add_contact(user_id, contact_id)
                contact_data_raw = messenger.redis_conn.hgetall(f'user:{contact_id}')
                contact_data = {k.decode(): v.decode() for k, v in contact_data_raw.items()}
                print(f"Added {contact_data['username']} (ID: {contact_data['user_id']}) to your contact list.")
            else:
                print("Invalid user ID. No user found with the given UUID.")
        elif option == '4':
            # List last 10 messages from a user
            print("Enter the UUID of the user whose messages you want to list:")
            contact_id = input()
            
            if messenger.redis_conn.exists(f'user:{contact_id}'):
                messages = messenger.list_user_messages(user_id)
                contact_messages = [msg for msg in messages if msg['sender_id'] == contact_id]
                last_10_messages = contact_messages[-10:]
                unseen_message_keys = []
                print(f"Last 10 messages from user {contact_id}:")
                for message in last_10_messages:
                    print(f"{message['timestamp']} - {message['message']}")
                    if message.get('seen', 'True') == 'False':
                        unseen_message_keys.append(message['message_key'])
                mark_messages_seen(messenger, unseen_message_keys)
            else:
                print("Invalid user ID. No user found with the given UUID.")
        elif option == '5':
            print("Saving user configuration...")
            save_user_config(user_id, messenger)
        elif option == '6':
            print("Exiting the chat...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    main()
