from config import BANNED_USERS_FILE
banned_users = set()
# Function to save banned users to file
def save_banned_users():
    with open(BANNED_USERS_FILE, 'w') as file:
        file.write("\n".join(str(uid) for uid in banned_users))
# Function to load banned users from file
def load_banned_users():
    global banned_users
    try:
        with open(BANNED_USERS_FILE, 'r') as file:
            banned_users = set(int(line.strip()) for line in file.readlines())
    except FileNotFoundError:
        open(BANNED_USERS_FILE, 'a').close()
# Function to ban a user
def ban_user(chat_id):
    banned_users.add(chat_id)
    save_banned_users()
# Function to unban a user
def unban_user(chat_id):
    if chat_id in banned_users:
        banned_users.remove(chat_id)
        save_banned_users()
# Function to check if a user is banned
def is_user_banned(chat_id):
    return chat_id in banned_users
