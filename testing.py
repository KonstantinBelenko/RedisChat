import redis
import json
import uuid
import time

class RedisMessenger:
    def __init__(self, host='redis-16800.c135.eu-central-1-1.ec2.cloud.redislabs.com', port=16800, db=0, password='S4iRnAr06pz18snSksieTKyumBCn8ISJ'):
        """Initialize the Redis connection."""
        try:
            self.redis_conn = redis.Redis(host=host, port=port, db=db, password=password)
        except redis.ConnectionError:
            print("Error: Unable to connect to Redis.")
            raise

    def create_user(self, username):
        """Create a user with a unique username."""
        existing_user = self.redis_conn.hget("usernames", username)
        if existing_user:
            raise ValueError("Error: Username already exists.")
        user_id = str(uuid.uuid4())
        user_key = f'user:{user_id}'
        user_data = {
            'username': username,
            'user_id': user_id,
            'created_at': time.time()
        }
        self.redis_conn.hset(user_key, mapping=user_data)
        self.redis_conn.hset("usernames", username, user_id)
        return user_id

    def send_message(self, sender_id, receiver_id, message):
        """Send a message from one user to another."""
        message_id = str(uuid.uuid4())
        message_key = f'message:{message_id}'
        timestamp = time.time()
        message_data = {
            'message_id': message_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'message': message,
            'timestamp': timestamp
        }
        self.redis_conn.hset(message_key, mapping=message_data)
        self.redis_conn.zadd(f'user_messages:{receiver_id}', {message_key: timestamp})
        return message_id

    def list_user_messages(self, user_id):
        """List messages for a user, ordered by timestamp."""
        messages = []
        message_keys = self.redis_conn.zrange(f'user_messages:{user_id}', 0, -1)
        for message_key in message_keys:
            message_data_raw = self.redis_conn.hgetall(message_key)
            message_data = {k.decode(): v.decode() for k, v in message_data_raw.items()}
            messages.append(message_data)
        return messages

    def list_all_users(self):
        """List all users in the system."""
        users = []
        cursor = '0'
        while cursor != 0:
            cursor, keys = self.redis_conn.scan(cursor=cursor, match='user:*')
            for key in keys:
                user_data_raw = self.redis_conn.hgetall(key)
                user_data = {k.decode(): v.decode() for k, v in user_data_raw.items()}
                users.append(user_data)
        return users


def main():
    messenger = RedisMessenger()

    try:
        user1_id = messenger.create_user('Alice')
        user2_id = messenger.create_user('Bob')
    except ValueError as e:
        print(e)
        return

    print(f"User 1 ID: {user1_id}")
    print(f"User 2 ID: {user2_id}")

    message_id = messenger.send_message(user1_id, user2_id, "Hello, Bob!")
    print(f"Sent message ID: {message_id}")

    messages = messenger.list_user_messages(user2_id)
    print("Messages for User 2:")
    for message in messages:
        print(json.dumps(message, indent=2))

    users = messenger.list_all_users()
    print("All users:")
    for user in users:
        print(json.dumps(user, indent=2))

if __name__ == '__main__':
    main()