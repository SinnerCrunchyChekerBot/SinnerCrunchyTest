import re
import time
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from bin0 import get_bin_info  # Importing the function from your script

def bin_lookup(update: Update, context: CallbackContext):
    start_time = time.time()
    
    # Extract BIN from user input
    if not context.args:
        update.message.reply_text("❌ Please provide a valid BIN (first 6 digits of a card).")
        return
    
    bin_number = re.findall(r'\d{6,}', context.args[0])
    if not bin_number:
        update.message.reply_text("❌ Please provide a valid BIN (first 6 digits of a card).")
        return
    
    bin_number = bin_number[0][:6]
    bin_data = get_bin_info(bin_number)

    if not bin_data:
        update.message.reply_text("❌ Invalid BIN or not found in the database.")
        return

    # Formatting the output
    response = (
        f"💳 <b>BIN Info:</b>\n"
        f"├ 🏦 <b>Bank:</b> {bin_data.get('bank_name', 'Unknown')}\n"
        f"├ 💳 <b>BIN:</b> <code>{bin_number}</code>\n"
        f"├ 🌍 <b>Country:</b> {bin_data.get('country', 'Unknown')} {bin_data.get('flag', '🏳')}\n"
        f"├ 🏷️ <b>Vendor:</b> {bin_data.get('vendor', 'Unknown')}\n"
        f"├ 🔍 <b>Type:</b> {bin_data.get('type', 'Unknown')}\n"
        f"├ 🔰 <b>Level:</b> {bin_data.get('level', 'Unknown')}\n"
        f"├ 💰 <b>Prepaid:</b> {bin_data.get('prepaid', 'Unknown')}\n"
        f"└ ⏳ <b>Time Taken:</b> <code>{round(time.time() - start_time, 2)}s</code>\n"
    )

    update.message.reply_text(response, parse_mode=ParseMode.HTML)


    

