from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import ADMIN_USER_IDS
from mongodb import users_collection
import threading
import time
import datetime
from others import require_registration

@require_registration
def set_premium(update: Update, context: CallbackContext):
    """Grants a user premium membership with a daily credit reset of 1000."""
    user = update.message.from_user
    if user.id not in ADMIN_USER_IDS:
        update.message.reply_text("🚫 You are not authorized to use this command!")
        return

    args = context.args
    if len(args) != 1:
        update.message.reply_text("Usage: /setpr <user_id>")
        return

    try:
        target_user_id = int(args[0])
    except ValueError:
        update.message.reply_text("❌ Invalid user ID format!")
        return

    users_collection.update_one(
        {"user_id": target_user_id}, 
        {"$set": {"is_premium": True, "credits": 1000, "last_reset": str(datetime.date.today())}},
        upsert=True
    )

    update.message.reply_text(f"✅ User `{target_user_id}` is now a premium member with 1000 credits daily!", parse_mode="Markdown")

    # Notify user
    context.bot.send_message(
        chat_id=target_user_id,
        text="🎉 You have been granted premium membership! Your credits will increase by 1000 daily.",
        parse_mode="Markdown"
    )

@require_registration
def unset_premium(update: Update, context: CallbackContext):
    """Removes premium membership from a user."""
    user = update.message.from_user
    if user.id not in ADMIN_USER_IDS:
        update.message.reply_text("🚫 You are not authorized to use this command!")
        return

    args = context.args
    if len(args) != 1:
        update.message.reply_text("Usage: /unsetpr <user_id>")
        return

    try:
        target_user_id = int(args[0])
    except ValueError:
        update.message.reply_text("❌ Invalid user ID format!")
        return

    users_collection.update_one(
        {"user_id": target_user_id}, 
        {"$unset": {"is_premium": "", "last_reset": ""}, "$set": {"credits": 50}}
    )

    update.message.reply_text(f"✅ User `{target_user_id}` is no longer a premium member! Credits set to 50.", parse_mode="Markdown")

    # Notify user
    context.bot.send_message(
        chat_id=target_user_id,
        text="⚠️ Your premium membership has been removed. Your credits have been reset to 50.",
        parse_mode="Markdown"
    )

def check_and_reset_credits():
    """Runs daily to add 1000 credits to premium users without resetting their balance."""
    while True:
        try:
            now = str(datetime.date.today())  # Store date as string
            users = users_collection.find({"is_premium": True})

            for user in users:
                user_id = user["user_id"]
                last_reset = user.get("last_reset", "")

                if last_reset != now:  # Update only if last reset is different
                    users_collection.update_one(
                        {"user_id": user_id},
                        {"$inc": {"credits": 1000}, "$set": {"last_reset": now}}
                    )
                    print(f"✅ Added 1000 credits to user {user_id} at {datetime.datetime.now()}")

            time.sleep(86400)  # Wait for 24 hours
        except Exception as e:
            print(f"❌ Error in credit reset thread: {e}")
            time.sleep(60)  # Retry in 1 minute if an error occurs

# Start the credit reset thread (only one instance runs)
reset_thread = threading.Thread(target=check_and_reset_credits, daemon=True)
reset_thread.start()

# Command Handlers
set_premium_handler = CommandHandler("setpr", set_premium)
unset_premium_handler = CommandHandler("unsetpr", unset_premium)
