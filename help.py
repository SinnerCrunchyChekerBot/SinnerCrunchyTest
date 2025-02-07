from lib2to3.pgen2.tokenize import TokenError
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from others import require_registration, store_user_id
from ban import is_user_banned

@require_registration
def help_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    message = (
    "❓ *Bot Help Guide:*\n\n"
    
    "👋 *Getting Started:* \n"
    "🔹 Use `/register` to start using the bot.\n\n"
    
    "💡 *Managing Your Credits:* \n"
    "🔹 Check your credit balance with `/credits`.\n"
    "🔹 Learn how the credit system works with `/howcrd`.\n\n"
    
    "📜 *Commands Overview:* \n"
    "🔹 View all available commands with `/cmds`.\n\n"
    
    "🆘 *Need Assistance?* \n"
    "🔹 If you need more help, feel free to contact the admin."
)

    update.message.reply_text(message, parse_mode="Markdown")

help_handler = CommandHandler("help", help_command)
