import logging
import random
import os
from flask import Flask
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InputMediaPhoto

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
names_list = []
images_list = []
MAX_NAMES = 20
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running"

# Command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot has started! Use .add to add your name.')

def add(update: Update, context: CallbackContext) -> None:
    if len(names_list) >= MAX_NAMES:
        update.message.reply_text('List is full! Try next game.')
        return
    name = ' '.join(context.args)
    if name:
        name = name.capitalize()
        if name not in names_list:
            names_list.append(name)
            update.message.reply_text(f'Added {name} to the list.')
            show_list(update, context)
        else:
            update.message.reply_text(f'{name} is already in the list.')
    else:
        update.message.reply_text('Usage: .add <name>')

def delete(update: Update, context: CallbackContext) -> None:
    name = ' '.join(context.args)
    if name:
        name = name.capitalize()
        if name in names_list:
            names_list.remove(name)
            update.message.reply_text(f'Removed {name} from the list.')
            show_list(update, context)
        else:
            update.message.reply_text(f'{name} is not in the list.')
    else:
        update.message.reply_text('Usage: .delete <name>')

def show_list(update: Update, context: CallbackContext) -> None:
    if names_list:
        reply_text = "Current list:\n" + "\n.join([f"{i+1}. {name}" for i, name in enumerate(names_list)])
        context.bot.send_message(chat_id=GROUP_ID, text=reply_text)
    else:
        update.message.reply_text('The list is empty.')

def pic(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type != 'private':
        return
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        images_list.append(photo_file_id)
        update.message.reply_text('Image added to the list.')
    else:
        update.message.reply_text('Please send an image with the .pic command.')

def remove(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type != 'private':
        return
    image_index = int(' '.join(context.args))
    if 0 <= image_index < len(images_list):
        images_list.pop(image_index)
        update.message.reply_text('Image removed from the list.')
    else:
        update.message.reply_text('Invalid image index. Please check the list and try again.')

def winner(update: Update, context: CallbackContext) -> None:
    if len(names_list) < MAX_NAMES:
        update.message.reply_text('List is not full yet.')
        return
    winner = random.choice(names_list)
    announcement = f'🎉 The winner is: {winner} 🎉\n\nPlease pick one prize and provide your address and phone number.'
    highlight_list = "\n".join([f"{i+1}. {name}" if name != winner else f"{i+1}. **{name}**" for i, name in enumerate(names_list)])
    
    # Send announcement and list
    context.bot.send_message(chat_id=GROUP_ID, text=f'{announcement}\n\n{highlight_list}')
    
    # Send images
    media_group = [InputMediaPhoto(image_id) for image_id in images_list]
    context.bot.send_media_group(chat_id=GROUP_ID, media=media_group)
    
    # Clear lists
    names_list.clear()
    images_list.clear()

def cmd(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type != 'private':
        return
    commands = """
    Available Commands:
    - .start: Start the bot
    - .add <name>: Add your name to the list
    - .delete <name>: Remove your name from the list
    - .winner: Announce the winner
    - .pic: Send an image to the bot (in private message)
    - .remove <index>: Remove an image from the list (in private message)
    - .cmd: Show this list of commands (in private message)
    """
    update.message.reply_text(commands)

def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Please refer to the pinned message or contact the admin for details.')

def main() -> None:
    """Start the bot."""
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

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
    # Start Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
