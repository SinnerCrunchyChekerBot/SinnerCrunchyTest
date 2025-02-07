from config import USER_IDS_FILE, REQUIRED_CHANNELS, ADMIN_USER_IDS
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
import logging
from ban import ban_user, unban_user
from mongodb import user_exists

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def require_registration(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        if not user_exists(user_id):
            update.message.reply_text("You are not registred, please use /register to proceed further")
            return
        return func(update, context)
    return wrapper

def store_user_id(user_id: int):
    if not os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'a') as file:
            file.write(f"{user_id}\n")
    else:
        with open(USER_IDS_FILE, 'r') as file:
            existing_ids = file.read().splitlines()

        if str(user_id) not in existing_ids:
            with open(USER_IDS_FILE, 'a') as file:
                file.write(f"{user_id}\n")



def check_membership(user_id: int, context: CallbackContext) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            channel_name = channel['name']
            logger.info(f"Attempting to check membership for user {user_id} in channel {channel_name}")
            member = context.bot.get_chat_member(chat_id=f'@{channel_name}', user_id=user_id)
            logger.info(f"Checking membership for {user_id} in {channel_name}: {member.status}")
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            logger.error(f"Error checking membership for {channel['name']}: {e}")
            return False
    return True


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data

    # Check if the user has joined all required channels
    if callback_data in ['start_joined', 'reset_joined']:
        if check_membership(user_id, context):
            query.answer("𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝗷𝗼𝗶𝗻𝗶𝗻𝗴 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 💋 !")

            # Image URL and caption for both scenarios
            video_url = 'https://motionbgs.com/media/4639/yor-forger-master-of-disguise.960x540.mp4'
            caption = "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 𝗥𝗲𝘀𝗲𝘁𝗕𝗼𝘁 ❤️‍🔥🕊!\n\n[≭] 𝗨𝘀𝗲 𝘁𝗵𝗲 /help 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝘁𝗼 𝗴𝗲𝘁 𝘀𝘁𝗮𝗿𝘁𝗲𝗱. \n[≭] 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 : @luciInvain \n[≭] 𝗠𝗮𝗶𝗻 : @GODTEST"

            # Inline keyboard buttons
            keyboard = [
                [InlineKeyboardButton("𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url="https://t.me/GODTEST")],
                [InlineKeyboardButton("𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥", url="https://t.me/luciinvain")]
            ]

            # Create the inline keyboard markup
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Edit the existing message to include the new image, caption, and buttons
            query.delete_message()  # Remove the previous message
            context.bot.send_video(
                chat_id=query.message.chat_id,
                video=video_url,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            query.answer("𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗻𝗼𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀.", show_alert=True)
            query.edit_message_text(text="𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗻𝗼𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.")

@require_registration
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('𝗣𝗿𝗼𝗰𝗲𝘀𝘀 𝗰𝗮𝗻𝗰𝗲𝗹𝗲𝗱.')
    return ConversationHandler.END


# Function to check if the user is an admin
def is_admin(user_id):
    return user_id in ADMIN_USER_IDS


@require_registration
# Admin function to ban a user
def ban(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if not is_admin(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗱𝗼 𝗻𝗼𝘁 𝗵𝗮𝘃𝗲 𝗮𝗰𝗲𝘀𝘀 𝘁𝗼 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return

    if len(context.args) != 1:
        update.message.reply_text("𝗣𝗹𝗲𝗮𝘀𝗲 𝗽𝗿𝗼𝘃𝗶𝗱𝗲 𝘁𝗵𝗲 𝘂𝘀𝗲𝗿 𝗜𝗗 𝘁𝗼 𝗯𝗮𝗻.")
        return

    try:
        chat_id_to_ban = int(context.args[0])
        ban_user(chat_id_to_ban)
        update.message.reply_text(f"𝗨𝘀𝗲𝗿 {chat_id_to_ban} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗯𝗮𝗻𝗻𝗲𝗱.")
    except ValueError:
        update.message.reply_text("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝘂𝘀𝗲𝗿 𝗜𝗗.")


@require_registration
# Admin function to unban a user
def unban(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if not is_admin(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗱𝗼 𝗻𝗼𝘁 𝗵𝗮𝘃𝗲 𝗮𝗰𝗲𝘀𝘀 𝘁𝗼 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return

    if len(context.args) != 1:
        update.message.reply_text("𝗣𝗹𝗲𝗮𝘀𝗲 𝗽𝗿𝗼𝘃𝗶𝗱𝗲 𝘁𝗵𝗲 𝘂𝘀𝗲𝗿 𝗜𝗗 𝘁𝗼 𝘂𝗻𝗯𝗮𝗻.")
        return

    try:
        chat_id_to_unban = int(context.args[0])
        unban_user(chat_id_to_unban)
        update.message.reply_text(f"𝗨𝘀𝗲𝗿 {chat_id_to_unban} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝘂𝗻𝗯𝗮𝗻𝗻𝗲𝗱.")
    except ValueError:
        update.message.reply_text("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝘂𝘀𝗲𝗿 𝗜𝗗.")
