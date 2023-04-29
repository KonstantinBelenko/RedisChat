# Redis Messenger

A simple Python messenger application using Redis as the datastore. The application allows creating users, sending messages between users, listing messages for a user, and listing all users.

```bash
Communication with reds -> redis_messenger.py
Communication with user -> chat.py
```

Schema:
```bash
user:<user_id> (HASH)
    - user_id (STRING): UUID of the user
    - username (STRING): Username of the user

usernames (HASH)
    - <username> (FIELD): User's username
    - <user_id> (VALUE): Corresponding user UUID

user_contacts:<user_id> (SET)
    - <contact_id> (STRING): UUID of a contact in the user's contact list

messages (LIST)
    - <message_key> (STRING): Key of the message stored in Redis

message:<message_id> (HASH)
    - message_id (STRING): UUID of the message
    - sender_id (STRING): UUID of the sender
    - recipient_id (STRING): UUID of the recipient
    - timestamp (STRING): Timestamp when the message was sent
    - message (STRING): Content of the message
    - seen (STRING): 'True' if the message has been seen, 'False' otherwise
```

## Redis Data Structures

The application uses the following Redis data structures:

1. **Hashes**: User data and message data are stored as Redis hashes. Each user has a unique hash with a key in the format `user:<user_id>`, and each message has a unique hash with a key in the format `message:<message_id>`. Additionally, there is a `usernames` hash that maps usernames to user IDs, ensuring unique usernames.

2. **Sorted Sets**: Messages for each user are stored as Redis sorted sets with keys in the format `user_messages:<user_id>`. The score for each message in the sorted set is its timestamp, allowing the messages to be ordered by the time they were sent.

## Function Descriptions

### `__init__(self, host='localhost', port=6379, db=0)`

This function initializes the Redis connection with the provided host, port, and db values.

### `create_user(self, username)`

This function creates a new user with a unique username.

1. Check if the username already exists in the `usernames` hash. If it does, raise a ValueError with an appropriate error message.
2. Generate a unique user ID using a UUID.
3. Create a user_key in the format `user:<user_id>`.
4. Set the user data (username, user_id, and created_at timestamp) in the Redis hash associated with the user_key.
5. Add the username and user_id to the `usernames` hash to ensure unique usernames.
6. Return the user_id.

### `send_message(self, sender_id, receiver_id, message)`

This function sends a message from one user to another.

1. Generate a unique message ID using a UUID.
2. Create a message_key in the format `message:<message_id>`.
3. Get the current timestamp.
4. Set the message data (message_id, sender_id, receiver_id, message, and timestamp) in the Redis hash associated with the message_key.
5. Add the message_key to the sorted set of messages for the receiver, using the timestamp as the score.
6. Return the message_id.

### `list_user_messages(self, user_id)`

This function lists messages for a user, ordered by timestamp.

1. Get the message_keys from the sorted set of messages for the user.
2. For each message_key:
   - Get the message data from the Redis hash associated with the message_key.
   - Decode the keys and values of the message data into strings.
   - Append the decoded message data to the messages list.
3. Return the messages list.

### `list_all_users(self)`

This function lists all users in the system.

1. Scan the Redis keys that match the pattern `user:*`.
2. For each user_key:
   - Get the user data from the Redis hash associated with the user_key.
   - Decode the keys and values of the user data into strings.
   - Append the decoded user data to the users list.
3. Return the users list.

## Running the Application

The `main()` function in the script demonstrates how to use the RedisMessenger class to create users, send messages, list messages for a user, and list all users. Run the script to see the application in action.
