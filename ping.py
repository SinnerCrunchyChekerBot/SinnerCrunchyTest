import time
from datetime import timedelta
from telegram import Update, Message
from telegram.ext import CallbackContext
from statistics calculate_uptime 
from others import require_registration, store_user_id
from ban import is_user_banned

# Track the bot's start time
BOT_START_TIME = time.time()


@require_registration
def ping(update: Update, context: CallbackContext):
    """
    Handles the /ping command to show the bot's status, uptime, latency, and statistics.
    """
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return

    # Record the start time before sending the initial message
    start_time = time.time()

    # Send an initial "Pinging..." message with a loading animation
    message: Message = update.message.reply_text("🏓 *Pinging...* ⏳", parse_mode="Markdown")

    # Measure latency after sending the message
    latency = round((time.time() - start_time) * 1000, 2)

    # Calculate uptime
    uptime = calculate_uptime()

    # Prepare the response message with a clean UI
    response_message = (
    "🎯 *Bot Status:* Online & Running Smoothly\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"📡 *Uptime:* `{uptime}`\n"
    f"⚡ *Latency:* `{latency} ms`\n"
    "🔹 *Response Speed:* Ultra Fast 🚀\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🤖 *Powered by:* [TEAM EHRA](https://t.me/bitchinhell)\n"
    "🔗 *Join for Updates and More!*"
)


    # Edit the initial "Pinging..." message with the final response
    message.edit_text(response_message, parse_mode="Markdown", disable_web_page_preview=True)
