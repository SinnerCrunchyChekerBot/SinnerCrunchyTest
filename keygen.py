import random
import string
import pymongo
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import MONGO_URL, DATABASE_NAME, ADMIN_USER_IDS, ADMIN_CHANNEL
from others import require_registration

# MongoDB setup
client = pymongo.MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
keys_collection = db["trial_keys"]

# Trial key types
KEY_TYPES = {
    "500c": {"name": "🎁 *500 Credits*", "credits": 500, "premium_days": 0},
    "1500c": {"name": "🎁 *1,500 Credits*", "credits": 1500, "premium_days": 0},
    "1d": {"name": "✨ *1-Day Premium*", "credits": 0, "premium_days": 1},
    "5k": {"name": "🔥 *1-Day Premium + 5,000 Credits*", "credits": 5000, "premium_days": 1},
    "3d5k": {"name": "👑 *3-Day Premium + 5,000 Credits*", "credits": 5000, "premium_days": 3},
}

# Generate a unique trial key
def generate_trial_key():
    prefix = "𝗦𝓲𝓷𝓷𝓮𝓻✘"
    key_body = "-".join(
        "".join(random.choices(string.ascii_letters + string.digits, k=4))
        for _ in range(4)
    )
    return f"{prefix}{key_body}"

# /genkeys <type> <count> (Admin-Only)
@require_registration
def genkeys(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Check if the user is an admin
    if user_id not in ADMIN_USER_IDS:
        update.message.reply_text("🚫 *Access Denied!* You are *not authorized* to use this command.", parse_mode="Markdown")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ *Usage:* `/genkeys <type> <count>`\n\nUse `/keys` to view available key types.", parse_mode="Markdown")
        return

    key_type = context.args[0]
    count = int(context.args[1])

    if key_type not in KEY_TYPES:
        update.message.reply_text("❌ *Invalid Key Type!*\nUse `/keys` to see available types.", parse_mode="Markdown")
        return

    generated_keys = []
    for _ in range(count):
        key = generate_trial_key()
        keys_collection.insert_one({
            "key": key,
            "type": key_type,
            "credits": KEY_TYPES[key_type]["credits"],
            "premium_days": KEY_TYPES[key_type]["premium_days"],
            "generated_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=4),
            "redeemed_by": None,
        })
        generated_keys.append(f"`{key}`")

    update.message.reply_text(
        f"✅ *Successfully Generated {count} Key(s)!*\n\n🎟️ *Key Type:* {KEY_TYPES[key_type]['name']}\n\n📜 *Generated Keys:* \n" + "\n".join(generated_keys),
        parse_mode="Markdown"
    )

# /keys (Admin-Only)
@require_registration
def keys(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Check if the user is an admin
    if user_id not in ADMIN_USER_IDS:
        update.message.reply_text("🚫 *Access Denied!* You are *not authorized* to use this command.", parse_mode="Markdown")
        return

    # Display available key types
    key_list = "\n".join(
        [f"🔑 *{KEY_TYPES[key]['name']}* - `{key}`" for key in KEY_TYPES]
    )
    
    update.message.reply_text(
        f"📋 *Available Trial Key Types:* \n\n{key_list}",
        parse_mode="Markdown"
    )
