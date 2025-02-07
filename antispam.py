import time
from telegram import Update
from telegram.ext import CallbackContext
from config import ADMIN_USER_IDS

# Dictionary to track user command usage
command_usage = {}

# Set of users who are exempt from anti-spam
spam_exempt_users = set()

# List of admin IDs
ADMIN_IDS = ADMIN_USER_IDS

# Dictionary to track temporarily blocked commands for each user
blocked_commands = {}

def is_spamming(user_id, command, cooldown=5):
    """
    Checks if the user is spamming a command and blocks further usage during cooldown.
    
    :param user_id: The Telegram user ID
    :param command: The command being used
    :param cooldown: Cooldown time in seconds (default: 5s)
    :return: True if the user is spamming, False otherwise
    """
    # Admins and exempt users bypass anti-spam
    if user_id in ADMIN_IDS or user_id in spam_exempt_users:
        return False

    current_time = time.time()
    user_key = f"{user_id}:{command}"

    # Check if this specific command is blocked for the user
    if user_key in blocked_commands and blocked_commands[user_key] > current_time:
        return True  # User is still in cooldown for this command

    # Check normal command usage cooldown
    if user_key in command_usage:
        last_used = command_usage[user_key]
        if current_time - last_used < cooldown:
            # Block the command for the user temporarily
            blocked_commands[user_key] = last_used + cooldown
            return True  # User is spamming

    command_usage[user_key] = current_time
    return False  # Not spamming

def handle_spam(update: Update, user_id, command, cooldown):
    """
    Handles anti-spam by sending a warning message and updating it dynamically with remaining cooldown time.
    The user is blocked from using the command until the cooldown expires.
    """
    user_key = f"{user_id}:{command}"
    last_used = command_usage.get(user_key, 0)
    remaining_time = int(cooldown - (time.time() - last_used))

    if remaining_time > 0:
        # Send the warning message immediately
        msg = update.message.reply_text(f"⚠️ Don't send commands too frequently! Cooldown: {remaining_time}s")

        while remaining_time > 0:
            time.sleep(1)  # Delay to avoid too many updates at once
            remaining_time -= 1
            try:
                # Edit the message to show remaining cooldown time
                msg.edit_text(f"❌ Anti-spam triggered! Try again in {remaining_time}s.")
            except:
                break  # If the message cannot be edited (deleted or expired), just exit

        # Unblock the command after cooldown expires
        blocked_commands.pop(user_key, None)

        return True  # Indicating that the user is blocked due to spamming
    return False  # Indicating that the user is not spamming

def spamapr(update: Update, context: CallbackContext):
    """Allows an admin to exempt a user from anti-spam."""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    args = context.args
    if not args:
        update.message.reply_text("Usage: /spamapr <user_id>")
        return

    try:
        target_user_id = int(args[0])
        spam_exempt_users.add(target_user_id)
        update.message.reply_text(f"✅ User `{target_user_id}` has been exempted from anti-spam.")
    except ValueError:
        update.message.reply_text("❌ Invalid user ID. Please enter a valid number.")

def spamupr(update: Update, context: CallbackContext):
    """Removes a user from the anti-spam exemption list."""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    args = context.args
    if not args:
        update.message.reply_text("Usage: /spamupr <user_id>")
        return

    try:
        target_user_id = int(args[0])
        if target_user_id in spam_exempt_users:
            spam_exempt_users.remove(target_user_id)
            update.message.reply_text(f"🚫 User `{target_user_id}` has been removed from the anti-spam exemption list.")
        else:
            update.message.reply_text(f"ℹ️ User `{target_user_id}` is not exempted from anti-spam.")
    except ValueError:
        update.message.reply_text("❌ Invalid user ID. Please enter a valid number.")
