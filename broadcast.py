import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from config import ADMIN_USER_IDS
from others import require_registration, store_user_id
from ban import *

# List of admin user IDs (imported from config)
admins = ADMIN_USER_IDS

# Global variables for mailing statistics
mailing_in_progress = False
sent_count = 0
failed_count = 0
total_users = 0
broadcast_thread = None


def is_admin(user_id):
    """Check if the user is an admin."""
    return user_id in admins

@require_registration
def broadcast(update: Update, context):
    """Start the broadcast process (Admin-only and DM-only)."""
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    global mailing_in_progress

    user_id = update.message.from_user.id

    if not is_admin(user_id):
        update.message.reply_text("🚫 *You are not authorized to use this command!*", parse_mode="Markdown")
        return

    if update.message.chat.type != "private":
        update.message.reply_text("🚫 *The /broadcast command can only be used in Direct Messages (DMs).*", parse_mode="Markdown")
        return

    if mailing_in_progress:
        update.message.reply_text("🚨 *A mailing is already in progress! Please wait until it's finished.* ⏳", parse_mode="Markdown")
        return

    mailing_in_progress = True
    update.message.reply_text(
        "📣 *Starting the Mailing Process...*\n\n"
        "Please send the message you'd like to broadcast to all users. 📝",
        parse_mode="Markdown"
    )


def receive_message_for_broadcast(update: Update, context):
    """Receives the message for broadcast and starts sending."""
    global mailing_in_progress, broadcast_thread

    user_id = update.message.from_user.id

    # Ignore all messages unless broadcast mode is active
    if not mailing_in_progress:
        return  

    if update.message.chat.type != "private":
        return

    if not is_admin(user_id):
        update.message.reply_text("🚫 *You are not authorized to send a broadcast message!*", parse_mode="Markdown")
        return

    message = update.message  # Save the forwarded message

    # Start broadcasting in a separate thread
    broadcast_thread = threading.Thread(target=start_broadcast, args=(context, message, user_id))
    broadcast_thread.start()

    update.message.reply_text("📤 *Broadcasting started...*\nUse /stopbroadcast or the button below to cancel.",
                              parse_mode="Markdown",
                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 STOP", callback_data="stop_broadcast")]]))


def start_broadcast(context, message, admin_id):
    """Broadcast messages in a separate thread."""
    global mailing_in_progress, sent_count, failed_count, total_users

    try:
        with open("user_ids.txt", "r") as f:
            user_ids = [line.strip() for line in f.readlines()]

        total_users = len(user_ids)
        sent_count = 0
        failed_count = 0

        # Send initial statistics message
        stats_message = context.bot.send_message(
            chat_id=admin_id,
            text="📤 *Sending messages...*\n\n"
                 "📝 *Messages Sent*: 0\n"
                 "❌ *Failed Messages*: 0\n"
                 f"📊 *Progress*: 0/{total_users}",
            parse_mode="Markdown"
        )

        # Store message ID for updating later
        stats_message_id = stats_message.message_id

        for idx, user_id in enumerate(user_ids):
            if not mailing_in_progress:
                break  # Stop broadcasting if canceled

            try:
                # Forward the message instead of re-sending text
                context.bot.forward_message(chat_id=user_id, from_chat_id=message.chat_id, message_id=message.message_id)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to send message to {user_id}: {e}")

            # Update statistics every 5 messages
            if (idx + 1) % 5 == 0:
                context.bot.edit_message_text(
                    chat_id=admin_id,
                    message_id=stats_message_id,
                    text=f"📤 *Sending messages...*\n\n"
                         f"📝 *Messages Sent*: {sent_count}\n"
                         f"❌ *Failed Messages*: {failed_count}\n"
                         f"📊 *Progress*: {idx + 1}/{total_users}",
                    parse_mode="Markdown"
                )

        # Send completion message
        context.bot.edit_message_text(
            chat_id=admin_id,
            message_id=stats_message_id,
            text=f"🎉 *Mailing Completed!* 📨\n\n"
                 f"📝 *Messages Sent*: {sent_count}\n"
                 f"❌ *Failed Messages*: {failed_count}\n\n"
                 "*Mailing process is finished.* Thank you for your patience! 🙏",
            parse_mode="Markdown"
        )

    except Exception as e:
        context.bot.send_message(
            chat_id=admin_id,
            text=f"❌ *An error occurred during the mailing process.*\n{e}",
            parse_mode="Markdown"
        )

    mailing_in_progress = False


@require_registration
def stop_broadcast(update: Update, context):
    """Stops the broadcast process."""
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
    global mailing_in_progress

    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    if not is_admin(user_id):
        update.message.reply_text("🚫 *You are not authorized to stop the broadcast!*", parse_mode="Markdown")
        return

    mailing_in_progress = False
    update.message.reply_text("🛑 *Broadcasting has been stopped.*", parse_mode="Markdown")


def handle_stop_button(update: Update, context):
    """Handles the stop button click."""
    
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        query.answer("🚫 You are not authorized to stop the broadcast.")
        return

    global mailing_in_progress
    mailing_in_progress = False
    query.edit_message_text("🛑 *Broadcasting has been stopped.*", parse_mode="Markdown")


# Handlers
broadcast_handler = CommandHandler("broadcast", broadcast)
receive_message_handler = MessageHandler(Filters.chat_type.private, receive_message_for_broadcast)
stop_broadcast_handler = CommandHandler("stopbroadcast", stop_broadcast)
stop_button_handler = CallbackQueryHandler(handle_stop_button, pattern="stop_broadcast")
