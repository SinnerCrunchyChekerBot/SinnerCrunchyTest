from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from others import require_registration,store_user_id
from ban import is_user_banned

@require_registration
def cmds_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    message = (
    "📜 *Available Commands:*\n\n"
    
    "👤 *User Commands:*\n"
    "✅ `/register` - Register to use the bot\n"
    "💰 `/credits` - Check your credit balance\n"
    "📜 `/cmds` - View all available commands\n"
    "ℹ️ `/howcrd` - Learn about the credit system\n"
    "🆘 `/help` - Get help using the bot\n\n"
    
    "⚡ *Checking Commands:*\n"
    "🔍 `/single <query>` - Perform a single check (5 credits)\n"
    "📊 `/mass <file>` - Perform a mass check (3 credits per check)\n"
    "🧹 `/clean <file>` - Clean invalid entries (10 credits)\n\n"

    "📊 *Bot Information:*\n"
    "📈 `/stats` - View bot statistics\n"
    "📡 `/ping` - Check bot response time\n\n"
    
    "🔐 *Admin Commands:*\n"
    "➕ `/addcr <user_id> <credits>` - Add credits to a user\n"
    "♻️ `/resetcr <user_id>` - Reset a user’s credits to 50\n"
    "📊 `/cr <user_id>` - View a user's full details\n"
)


    update.message.reply_text(message, parse_mode="Markdown")

cmds_handler = CommandHandler("cmds", cmds_command)
