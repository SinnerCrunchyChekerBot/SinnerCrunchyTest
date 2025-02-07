import subprocess
import sys

def ModulesAutoBySinner():
    """
    Installs the required modules. If a `ModuleNotFoundError` is raised, the missing module
    will be dynamically installed and the script will continue execution.
    """
    required_modules = [
        "requests",
        # "python-telegram-bot==13.7",
        "random",
        "os",
        "time",
        "pymongo",
        "datetime",
        "string",
        "logging"   #add more modules
    ]
    for module in required_modules:
        try:
            __import__(module)
        except ModuleNotFoundError:
            print(f"Module '{module}' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
    try:
        print("All known modules installed. Verifying runtime imports...")
        import logging
        import random
        import os
        from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
    except ModuleNotFoundError as e:
        missing_module = e.name
        print(f"Detected missing module '{missing_module}'. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", missing_module])

        print(f"Module '{missing_module}' installed successfully. Restarting verification...")