import logging
import random
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask, jsonify
import asyncio

# Initialize Flask app
flask_app = Flask(__name__)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Bot token from environment variables
GROUP_ID = os.getenv('GROUP_ID')  # Group ID from environment variables

# List for participants and images
participants = []
MAX_PARTICIPANTS = 20
image_list = []

# Function to handle adding a name to the list
def add_participant(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Please provide a name after the .add command, like .add <your_name>.')
        return
    
    name = ' '.join(context.args).title()

    if len(participants) >= MAX_PARTICIPANTS:
        update.message.reply_text(f'The list is full. Try again in the next game!')
        return

    if name in participants:
        update.message.reply_text(f'{name} is already in the list.')
        return

    participants.append(name)
    update.message.reply_text(f'Added {name} to the list!')
    display_participants(update)

# Function to handle removing a name from the list
def remove_participant(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Please provide a name after the .remove command, like .remove <your_name>.')
        return

    name = ' '.join(context.args).title()

    if name not in participants:
        update.message.reply_text(f'{name} is not in the list.')
        return

    participants.remove(name)
    update.message.reply_text(f'Removed {name} from the list.')
    display_participants(update)

# Function to announce the winner
def announce_winner(update: Update, context: CallbackContext) -> None:
    if len(participants) < MAX_PARTICIPANTS:
        update.message.reply_text('List not completed yet! There must be 20 participants before drawing a winner.')
        return

    winner = random.choice(participants)
    update.message.reply_text(f'🎉🎉🎉 The winner is... {winner}!!! 🎉🎉🎉')

    if image_list:
        display_images_group(update)

    update.message.reply_text(f"Congratulations {winner}! 🎉\n\nPlease pick a prize from the image list above and send me your address and phone number.")

    participants.clear()

# Function to display the image list
def display_images_group(update: Update) -> None:
    num_images = len(image_list)
    images_per_row = (num_images + 1) // 2  # Calculate the number of images per row

    first_row = "\n".join([f"Image {i+1}: {image_list[i]}" for i in range(images_per_row)])
    second_row = "\n".join([f"Image {i+1}: {image_list[i]}" for i in range(images_per_row, num_images)])

    update.message.reply_text(f"Images (Row 1):\n{first_row}")
    if second_row:
        update.message.reply_text(f"Images (Row 2):\n{second_row}")

# Function to display the participants list
def display_participants(update: Update) -> None:
    if not participants:
        update.message.reply_text("The participants list is empty.")
        return

    participants_text = "\n".join([f"{i+1}. {participant}" for i, participant in enumerate(participants)])
    update.message.reply_text(f"Current Participants:\n{participants_text}")

# Function to handle invalid commands
def handle_invalid_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Invalid command! Please use .add <name>, .remove <name>, or .winner.')

# Function to handle adding an image to the list via direct message
def add_image(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id != update.message.from_user.id:
        return

    if update.message.photo:
        image_url = update.message.photo[-1].file_id
        image_list.append(image_url)
        update.message.reply_text(f'Added image to the list! Total images: {len(image_list)}')
    else:
        update.message.reply_text('Please send a photo to add to the list.')

# Function to handle deleting an image from the list
def delete_image(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id != update.message.from_user.id:
        return

    if len(context.args) == 0:
        update.message.reply_text('Please provide the image index to delete, like .delete <index>.')
        return

    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(image_list):
            update.message.reply_text('Invalid index. Please provide a valid image index.')
            return
        image_list.pop(index)
        update.message.reply_text(f'Image removed! Total images: {len(image_list)}')
    except ValueError:
        update.message.reply_text('Please provide a valid integer index for the image to delete.')

# Function to show all available commands
def show_commands(update: Update, context: CallbackContext) -> None:
    commands = (
        ".add <name> - Add a name to the participant list (group game)\n"
        ".remove <name> - Remove a name from the participant list (group game)\n"
        ".winner - Draw a random winner from the participant list\n"
        ".pic - Send a photo in direct message to add to the image list\n"
        ".delete <index> - Delete an image from the image list by index\n"
        ".cmd - Show available commands"
    )
    update.message.reply_text(commands)

# Function to ignore non-text messages (like photos, videos, etc.)
def ignore_non_text_messages(update: Update, context: CallbackContext) -> None:
    pass

# Flask endpoint to keep the service running
@flask_app.route("/")
def index():
    return jsonify({"status": "ok"})

# Main asynchronous function to start the Telegram bot
async def main():
    if not BOT_TOKEN:
        raise ValueError("No BOT_TOKEN found in environment variables.")
    
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("add", add_participant))
    application.add_handler(CommandHandler("remove", remove_participant))
    application.add_handler(CommandHandler("winner", announce_winner))
    application.add_handler(CommandHandler("cmd", show_commands))
    application.add_handler(CommandHandler("delete", delete_image))
    application.add_handler(CommandHandler("images", display_images_group))

    application.add_handler(MessageHandler(filters.PHOTO, add_image))
    application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, ignore_non_text_messages))

    application.add_handler(CommandHandler('.*', handle_invalid_command))

    await application.run_polling()

# Run the bot inside the Flask app
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    flask_app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
