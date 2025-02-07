from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import ADMIN_CHANNEL, tok  # Ensure ADMIN_CHANNEL is "@fulfilledbydeath"
from mongodb import add_user, user_exists
from datetime import datetime
from others import store_user_id
from ban import is_user_banned

def register_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name or "N/A"
    last_name = user.last_name or "N/A"
    username = f"@{user.username}" if user.username else "N/A"
    is_premium = getattr(user, "is_premium", False)
    date_joined = datetime.utcnow()
    credits = 250  # Registration bonus

    # Generate clickable profile link
    profile_url = f"[{first_name}](tg://user?id={user_id})"

    if user_exists(user_id):
        update.message.reply_text("You are already registered!")
        return

    user_data = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "is_premium": is_premium,
        "TelegramPremium": is_premium,
        "credits": credits,
        "date_joined": date_joined
    }

    add_user(user_data)

    success_message = (
    f"✅ *Registration Successful!*\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"👤 *Name:* {profile_url}\n"
    f"🏷 *User ID:* `{user_id}`\n"
    f"🎁 *Credits:* `{credits} Credits`\n"
    f"📅 *Date Joined:* {date_joined.strftime('%Y-%m-%d %H:%M')}\n\n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"📌 *250 credits have been credited as\n your registration bonus.*\n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"ℹ️ *To learn more about the \ncredit system, use* `/howcrd`\n"
    f"🛠 *To learn more about the bot and\n its commands, use* `/start` *or* `/cmds`\n"
    f"❓ *For assistance, use* `/help` *to get\n more information about how\n to use the bot.*"
)


    update.message.reply_text(success_message, parse_mode="Markdown")

    admin_message = (
    f"🚀 *New User Registered!*\n\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"👤 *Name:* {profile_url} {last_name}\n"
    f"🏷 *User ID:* `{user_id}`\n"
    f"📛 *Username:* {username}\n"
    f"💎 *Telegram Premium:* {'Yes' if is_premium else 'No'}\n"
    f"🎁 *Credits:* `{credits}`\n"
    f"⛔ *Restrictions:* None\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"📅 *Date Joined:* {date_joined.strftime('%Y-%m-%d %H:%M')}\n"
)


    # Use parse_mode="Markdown"
    context.bot.send_message(chat_id=ADMIN_CHANNEL, text=admin_message, parse_mode="Markdown")
