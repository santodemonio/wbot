import logging
import random
import os
import socket
from flask import Flask
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InputMediaPhoto
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Global variables
names_list = []
images_list = []
MAX_NAMES = 20
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Flask app without any routes
app = Flask(__name__)

# Command handlers (omitting handlers for brevity)

def find_available_port(start_port=5000, max_retries=10):
    """Finds an available port starting from `start_port`."""
    for port in range(start_port, start_port + max_retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            if result != 0:  # Port is not in use
                return port
    return start_port  # Default to start port if no port is available

def run_flask():
    # Automatically find the first available port
    port = find_available_port()
    app.run(host='0.0.0.0', port=port, use_reloader=False)  # Note: Flask's built-in server will not be used in production, Gunicorn will take over

def main():
    """Start the bot."""
    logger.debug("Starting the bot.")
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("winner", winner))
    dispatcher.add_handler(CommandHandler("remove", remove))
    dispatcher.add_handler(CommandHandler("cmd", cmd))
    dispatcher.add_handler(MessageHandler(Filters.photo & Filters.private, pic))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown))
    
    # Handlers to ignore media in group chats
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.private, ignore_media))
    dispatcher.add_handler(MessageHandler(Filters.voice & ~Filters.private, ignore_media))

    # Start polling with a small delay to prevent the bot from shutting down
    while True:
        try:
            updater.start_polling(timeout=30, clean=False)
            updater.idle()
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            time.sleep(5)  # Sleep for a bit and retry polling

if __name__ == '__main__':
    # Use ThreadPoolExecutor to manage threads more efficiently
    with ThreadPoolExecutor() as executor:
        # Run Flask and the Telegram bot concurrently
        executor.submit(run_flask)
        executor.submit(main)
