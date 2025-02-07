from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from others import require_registration, store_user_id
from ban import is_user_banned

@require_registration
def how_credits_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    message = (
    "💰 *Credit System Overview:*\n\n"
    
    "🎉 *Welcome Bonus:* \n"
    "➤ New users receive `50 credits` upon registration.\n\n"
    
    "🛠 *Command Costs:*\n"
    "🔹 `/single <query>` ➝ `5 credits` per check\n"
    "🔹 `/mass <file>` ➝ `3 credits` per check\n"
    "🔹 `/clean <file>` ➝ `10 credits` per clean\n\n"
    
    "💎 *Premium Perks:* \n"
    "🚀 Premium users enjoy *`1000 credits` reset daily!*\n\n"
    
    "🎁 *Bonus Rewards:* \n"
    "🔑 *Trial Key Redemption:* Use special trial keys to unlock extra credits!\n"
    "💵 *Admin Rewards:* Admins may grant bonus credits based on activity.\n\n"
    
    "⚡ *Use your credits wisely and enjoy seamless checking!*"
)

    update.message.reply_text(message, parse_mode="Markdown")

how_credits_handler = CommandHandler("howcrd", how_credits_command)
