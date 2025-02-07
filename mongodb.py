from pymongo import MongoClient
from config import MONGO_URL, DATABASE_NAME
import datetime

# MongoDB Connection
client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
users_collection = db["users"]
keys_collection = db["trial_keys"]

def user_exists(user_id):
    return users_collection.find_one({"user_id": user_id}) is not None

def add_user(user_data):
    if not user_exists(user_data["user_id"]):
        user_data["credits"] = 250  # Assign welcome credits
        user_data["premium_until"] = None  # No premium by default
        users_collection.insert_one(user_data)

def get_user_credits(user_id):
    user = users_collection.find_one({"user_id": user_id}, {"credits": 1})
    return user.get("credits", 0) if user else 0

def deduct_credits(user_id, amount):
    user = users_collection.find_one({"user_id": user_id})
    if user and user.get("credits", 0) >= amount:
        users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -amount}}
        )
        return True  # Deduction successful
    return False  # Insufficient credits

def has_premium(user_id):
    user = users_collection.find_one({"user_id": user_id}, {"premium_until": 1})
    if user and user.get("premium_until"):
        return user["premium_until"] > datetime.datetime.utcnow()
    return False

def grant_premium(user_id, hours):
    new_premium_until = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"premium_until": new_premium_until}}
    )
    return new_premium_until

def add_credits(user_id, amount):
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": amount}}
    )

def redeem_trial_key(user_id, key):
    key_data = keys_collection.find_one({"key": key})

    if not key_data:
        return "❌ Invalid or expired key."

    if key_data["status"] != "unused":
        return "⚠️ This key has already been used."

    if key_data["expires_at"] < datetime.datetime.utcnow():
        keys_collection.update_one({"key": key}, {"$set": {"status": "expired"}})
        return "⌛ This key has expired."

    # Check key type and apply rewards
    TRIAL_TYPES = {
        "500c": {"credits": 500, "premium_hours": 0},
        "1500c": {"credits": 1500, "premium_hours": 0},
        "1d": {"credits": 0, "premium_hours": 24},
        "5k": {"credits": 5000, "premium_hours": 24},
        "3d5k": {"credits": 5000, "premium_hours": 72},
    }

    key_type = key_data["type"]
    if key_type not in TRIAL_TYPES:
        return "❌ Invalid key type."

    credits_to_add = TRIAL_TYPES[key_type]["credits"]
    premium_hours = TRIAL_TYPES[key_type]["premium_hours"]

    if credits_to_add > 0:
        add_credits(user_id, credits_to_add)

    if premium_hours > 0:
        grant_premium(user_id, premium_hours)

    # Mark key as used
    keys_collection.update_one({"key": key}, {"$set": {"status": "used", "used_by": user_id, "used_at": datetime.datetime.utcnow()}})

    success_message = "✅ *Trial Key Redeemed Successfully!*\n"
    if credits_to_add > 0:
        success_message += f"💰 *Credits Added:* `{credits_to_add}`\n"
    if premium_hours > 0:
        success_message += f"👑 *Premium Activated for:* `{premium_hours}` hours\n"

    return success_message
