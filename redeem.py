import pymongo
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import MONGO_URL, DATABASE_NAME, ADMIN_CHANNEL
from others import require_registration, store_user_id
from ban import is_user_banned

# MongoDB setup
client = pymongo.MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
keys_collection = db["trial_keys"]
users_collection = db["users"]

# /redeem <key>
@require_registration
def redeem(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "N/A"
    first_name = update.message.from_user.first_name
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return

    if not context.args:
        update.message.reply_text("⚠️ *Usage:* `/redeem <trial_key>`", parse_mode="Markdown")
        return

    key = context.args[0]

    # Check if the key exists
    key_data = keys_collection.find_one({"key": key})

    if not key_data:
        update.message.reply_text("❌ *Invalid Key!* Please check and try again.", parse_mode="Markdown")
        return

    # Check if the key has expired
    if key_data["expires_at"] < datetime.utcnow():
        update.message.reply_text("⏳ *This key has expired and can no longer be used.*", parse_mode="Markdown")
        return

    # Check if the key has already been used
    if key_data["redeemed_by"]:
        update.message.reply_text("⚠️ *This key has already been redeemed by another user!*", parse_mode="Markdown")
        return

    # Check if user has redeemed 2 keys today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    user_redemptions = keys_collection.count_documents({
        "redeemed_by": user_id,
        "redeemed_at": {"$gte": today_start},
    })

    if user_redemptions >= 3:
        update.message.reply_text("🚫 *You can only redeem 3 trial keys per day!*", parse_mode="Markdown")
        return

    # Fetch user from the database
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        update.message.reply_text("⚠️ *You need to register first using* `/register`.", parse_mode="Markdown")
        return

    # Update user credits and premium status
    new_credits = user.get("credits", 0) + key_data["credits"]
    premium_days = key_data["premium_days"]

    # Calculate new premium expiry
    if premium_days > 0:
        if "premium_expiry" in user and user["premium_expiry"] > datetime.utcnow():
            new_premium_expiry = user["premium_expiry"] + timedelta(days=premium_days)
        else:
            new_premium_expiry = datetime.utcnow() + timedelta(days=premium_days)
    else:
        new_premium_expiry = user.get("premium_expiry", datetime.utcnow())

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"credits": new_credits, "premium_expiry": new_premium_expiry}}
    )

    # Mark the key as redeemed
    keys_collection.update_one({"key": key}, {"$set": {"redeemed_by": user_id, "redeemed_at": datetime.utcnow()}})

    # Send confirmation message
    response = (
        f"🎉 *Redemption Successful!*\n\n"
        f"🎟️ *Key Type:* `{key_data['type']}`\n"
        f"💰 *Credits Added:* `{key_data['credits']}`\n"
        f"👑 *Premium Days:* `{premium_days}`\n"
        f"📊 *New Credit Balance:* `{new_credits}`\n"
    )
    
    if premium_days > 0:
        response += f"⏳ *Premium Expiry:* `{new_premium_expiry.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n"

    update.message.reply_text(response, parse_mode="Markdown")

    # Notify Admins
    context.bot.send_message(
        chat_id=ADMIN_CHANNEL,
        text=(
            f"🔔 *Key Redeemed!*\n\n"
            f"👤 *User:* `{first_name}` (@{username})\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"🎟️ *Key Type:* `{key_data['type']}`\n"
            f"💰 *Credits:* `{key_data['credits']}`\n"
            f"👑 *Premium Days:* `{premium_days}`\n"
        ),
        parse_mode="Markdown"
    )

# Register the command
redeem_handler = CommandHandler("redeem", redeem)
