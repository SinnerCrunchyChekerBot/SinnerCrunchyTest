import time
from datetime import timedelta
from telegram import Update
from telegram.ext import CallbackContext
from mongodb import users_collection
from others import require_registration, store_user_id  # Import MongoDB connection
from ban import is_user_banned

# Track bot start time
BOT_START_TIME = time.time()
BOT_VERSION = "v2.69"



def calculate_uptime():
    """
    Calculate and return the bot's uptime in HH:MM:SS format.
    """
    uptime_seconds = int(time.time() - BOT_START_TIME)
    return str(timedelta(seconds=uptime_seconds))

def get_banned_users_count():
    """
    Read the number of banned users from banned_users.txt.
    """
    try:
        with open("banned_users.txt", "r") as file:
            banned_users = file.readlines()
        return len(banned_users)  # Count total banned users
    except FileNotFoundError:
        return 0  # If the file doesn't exist, return 0


@require_registration
def statistics(update: Update, context: CallbackContext):
    """
    Handles the /statistics command to show real-time bot statistics.
    """
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    global command_usage

    # Fetch real-time data from MongoDB
    total_users = users_collection.count_documents({})  # Total registered users
    premium_users = users_collection.count_documents({"is_premium": True})  # Premium members
    active_users_today = users_collection.count_documents({"last_active": str(time.strftime("%Y-%m-%d"))})  # Active users today
    banned_users = get_banned_users_count()  # Get banned users count from file

    # Calculate bot uptime
    uptime = calculate_uptime()


    # Response message with improved UI
    response_message = (
    "📊 *Bot Performance Statistics*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"✅ *Bot Status:* Online & Running ⚡\n"
    f"⏳ *Uptime:* `{uptime}`\n"
    f"📌 *Bot Version:* `{BOT_VERSION}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    
    f"👥 *Total Users:* `{total_users}`\n"
    f"👑 *Premium Users:* `{premium_users}`\n"
    f"🚫 *Banned Users:* `{banned_users}`\n"
    f"📊 *Active Users Today:* `{active_users_today}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    
    "🤖 *Powered by:* [TEAM EHRA](https://t.me/GODTEST)\n"
    "🔗 *Stay Updated & Join Us!*"
)


    # Send the response
    update.message.reply_text(response_message, parse_mode="Markdown", disable_web_page_preview=True)
