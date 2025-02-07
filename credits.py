from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import ADMIN_USER_IDS
from mongodb import users_collection
from others import store_user_id, require_registration
from ban import is_user_banned
import datetime

# Function to get user credits
def get_user_credits(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user.get("credits", 0) if user else 0

def update_user_credits(user_id, credits):
    """Update the user's credit balance in MongoDB."""
    users_collection.update_one({"user_id": user_id}, {"$set": {"credits": credits}})

# Command to check user's credits and full details
@require_registration
def credits_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name

    store_user_id(user_id)

    if is_user_banned(user_id):
        update.message.reply_text("❌ *You are restricted from using this bot. Contact the developer for assistance.*", parse_mode="Markdown")
        return
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        update.message.reply_text(
        f"*Hello* [{first_name}](tg://user?id={user_id})*!. You Are Unregistered, You Have To Register In Order To Use The Bot At Its Full Potential. Use /register Command To Register And Proceed Furthur.*", parse_mode="Markdown"
        )
        return
    first_name = user_data.get("first_name", "N/A")
    last_name = user_data.get("last_name", "N/A")
    username = user_data.get("username", "N/A")
    is_premium = user_data.get("is_premium", False)
    credits = user_data.get("credits", 0)
    date_joined = user_data.get("date_joined", "Unknown")
    restrictions = user_data.get("restrictions", "None")
    last_reset = user_data.get("last_reset", "Never")
    profile_url = f"[{first_name}](tg://user?id={user_id})"
    premium_status = "✅ Yes" if is_premium else "❌ No"
    message = (
    f"🔍 *User Information (Admin View):*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"🏷 *User ID:* `{user_id}`\n"
    f"📛 *Username:* `{username}`\n"
    f"👤 *Name:* {profile_url} {last_name}\n"
    f"💎 *Premium Status:* {premium_status}\n"
    f"🎁 *Credits:* `{credits}`\n"
    f"📅 *Last Reset:* `{last_reset}`\n"
    f"⛔ *Restrictions:* `{restrictions}`\n"
    f"📆 *Date Joined:* `{date_joined}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
)

    update.message.reply_text(message, parse_mode="Markdown")
# Admin command to add credits to a user
@require_registration
def add_credits_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    store_user_id(user_id)

    if is_user_banned(user_id):
        update.message.reply_text("❌ *You are restricted from using this bot. Contact the developer for assistance.*", parse_mode="Markdown")
        return
    if user.id not in ADMIN_USER_IDS:
        update.message.reply_text("🚫 *You are not authorized to use this command!*", parse_mode="Markdown")
        return
    args = context.args
    if len(args) != 2:
        update.message.reply_text("*Usage: /addcr <user_id> <credits>*", parse_mode="Markdown")
        return
    try:
        target_user_id = int(args[0])
        credits_to_add = int(args[1])
    except ValueError:
        update.message.reply_text("❌ *Invalid input! Use /addcr <user_id> <credits>*", parse_mode="Markdown")
        return
    user_data = users_collection.find_one({"user_id": target_user_id})
    if not user_data:
        update.message.reply_text("❌ *User not found in the database!*",parse_mode="Markdown")
        return
    users_collection.update_one({"user_id": target_user_id}, {"$inc": {"credits": credits_to_add}})
    new_balance = get_user_credits(target_user_id)
    update.message.reply_text(f"✅ *Successfully added* `{credits_to_add}` *credits to* `{target_user_id}`!\n*New Balance:* `{new_balance}`", parse_mode="Markdown")
    context.bot.send_message(
        chat_id=target_user_id,
        text=f"🎉 *You have received* `{credits_to_add}` *credits from an admin!*\n*Your new balance is* `{new_balance}` *credits.*",
        parse_mode="Markdown"
    )
@require_registration
def reset_credits_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    store_user_id(user_id)

    if is_user_banned(user_id):
        update.message.reply_text("❌ *You are restricted from using this bot. Contact the developer for assistance.*", parse_mode="Markdown")
        return
    if user.id not in ADMIN_USER_IDS:
        update.message.reply_text("❌ *You are not authorized to use this command.*", parse_mode="Markdown")
        return
    try:
        target_user_id = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("❌ *Usage: /resetcr <user_id>*", parse_mode="Markdown")
        return
    if not users_collection.find_one({"user_id": target_user_id}):
        update.message.reply_text("❌ *User not found.*", parse_mode="Markdown")
        return
    update_user_credits(target_user_id, 50)
    update.message.reply_text(f"✅ *Reset credits for user* `{target_user_id}` *to* `0`.", parse_mode="Markdown")
    context.bot.send_message(
        chat_id=target_user_id,
        text=f"*Your credits were reset by an admin, you new balance is 0 credits.*",
        parse_mode="Markdown"
    )
def deduct_credits(user_id, amount):
    """Deducts credits from the user's balance."""
    user = users_collection.find_one({"user_id": user_id})
    if user and user["credits"] >= amount:
        users_collection.update_one({"user_id": user_id}, {"$inc": {"credits": -amount}})
        return True
    return False
# Command Handlers
credits_handler = CommandHandler("credits", credits_command)
add_credits_handler = CommandHandler("addcr", add_credits_command)
reset_credits_handler = CommandHandler("resetcr", reset_credits_command)


# Command to check full user details (for admins only)
@require_registration
def cr_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    store_user_id(user_id)

    if is_user_banned(user_id):
        update.message.reply_text("❌ *You are restricted from using this bot. Contact the developer for assistance.*", parse_mode="Markdown")
        return

    if user.id not in ADMIN_USER_IDS:
        update.message.reply_text("🚫 *You are not authorized to use this command!*", parse_mode="Markdown")
        return

    args = context.args
    if len(args) != 1:
        update.message.reply_text("❌ *Usage: /cr <user_id>*", parse_mode="Markdown")
        return

    try:
        target_user_id = int(args[0])
    except ValueError:
        update.message.reply_text("❌ *Invalid user ID format! Use /cr <user_id>*", parse_mode="Markdown")
        return

    user_data = users_collection.find_one({"user_id": target_user_id})
    if not user_data:
        update.message.reply_text("❌ *User not found in the database!*", parse_mode="Markdown")
        return

    first_name = user_data.get("first_name", "N/A")
    last_name = user_data.get("last_name", "N/A")
    username = user_data.get("username", "N/A")
    is_premium = user_data.get("is_premium", False)
    credits = user_data.get("credits", 0)
    date_joined = user_data.get("date_joined", "Unknown")
    restrictions = user_data.get("restrictions", "None")
    last_reset = user_data.get("last_reset", "Never")

    profile_url = f"[{first_name}](tg://user?id={target_user_id})"
    premium_status = "✅ Yes (1000 Credits Reset Daily)" if is_premium else "❌ No"

    message = (
    f"🔍 *User Information (Admin View):*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"🏷 *User ID:* `{target_user_id}`\n"
    f"📛 *Username:* `{username}`\n"
    f"👤 *Name:* {profile_url} {last_name}\n"
    f"💎 *Premium Status:* {premium_status}\n"
    f"🎁 *Credits:* `{credits}`\n"
    f"📅 *Last Reset:* `{last_reset}`\n"
    f"⛔ *Restrictions:* `{restrictions}`\n"
    f"📆 *Date Joined:* `{date_joined}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
)


    update.message.reply_text(message, parse_mode="Markdown")

# Command Handler for /cr command
cr_handler = CommandHandler("cr", cr_command)

