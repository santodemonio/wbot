import logging
import random
import os
from telegram import Update, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # Updated import for filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# This will store the list of names for the group game
participants = []
MAX_PARTICIPANTS = 20

# This will store the list of images (indexed)
image_list = []

# Read environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Bot token from environment variables
GROUP_ID = os.getenv('GROUP_ID')  # Group ID from environment variables

# Function to handle adding a name to the list for the group lottery
def add_participant(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Please provide a name after the .add command, like .add <your_name>.')
        return
    
    # Capitalize the first letter of each word in the name
    name = ' '.join(context.args).title()

    if len(participants) >= MAX_PARTICIPANTS:
        update.message.reply_text(f'The list is full. Try again in the next game!')
        return

    if name in participants:
        update.message.reply_text(f'{name} is already in the list.')
        return

    participants.append(name)
    update.message.reply_text(f'Added {name} to the list!')

    # Send the current list of participants with serial numbers
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

    # Send the current list of participants with serial numbers
    display_participants(update)


# Function to handle announcing the winner
def announce_winner(update: Update, context: CallbackContext) -> None:
    if len(participants) < MAX_PARTICIPANTS:
        update.message.reply_text('List not completed yet! There must be 20 participants before drawing a winner.')
        return

    winner = random.choice(participants)
    update.message.reply_text(f'🎉🎉🎉 The winner is... {winner}!!! 🎉🎉🎉')

    # Send the image list to the group and ask the winner to pick a prize and provide contact info
    if image_list:
        # Display image list in the group (two rows)
        display_images_group(update)

    update.message.reply_text(f"Congratulations {winner}! 🎉\n\n"
                              "Please pick a prize from the image list above and send me your address and phone number.")

    # Clear the participants list for the next game
    participants.clear()


# Function to display the image list in two rows in the group
def display_images_group(update: Update) -> None:
    """Displays the image list in two rows in the group."""
    num_images = len(image_list)
    images_per_row = (num_images + 1) // 2  # Calculate the number of images per row

    first_row = "\n".join([f"Image {i+1}: {image_list[i]}" for i in range(images_per_row)])
    second_row = "\n".join([f"Image {i+1}: {image_list[i]}" for i in range(images_per_row, num_images)])

    # Send both rows to the group
    update.message.reply_text(f"Images (Row 1):\n{first_row}")
    if second_row:
        update.message.reply_text(f"Images (Row 2):\n{second_row}")


# Function to display the participants list with serial numbers
def display_participants(update: Update) -> None:
    """Displays the participants list with serial numbers and capitalized names."""
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
    """Handles the .pic command, adds an image to the list."""
    if update.message.chat.id != update.message.from_user.id:  # Only allow DMs
        return

    if update.message.photo:
        image_url = update.message.photo[-1].file_id  # Get the highest resolution photo
        image_list.append(image_url)
        update.message.reply_text(f'Added image to the list! Total images: {len(image_list)}')
    else:
        update.message.reply_text('Please send a photo to add to the list.')


# Function to handle deleting an image from the list
def delete_image(update: Update, context: CallbackContext) -> None:
    """Handles the .delete command, removes an image from the list."""
    if update.message.chat.id != update.message.from_user.id:  # Only allow DMs
        return

    if len(context.args) == 0:
        update.message.reply_text('Please provide the image index to delete, like .delete <index>.')
        return

    try:
        index = int(context.args[0]) - 1  # Convert to 0-based index
        if index < 0 or index >= len(image_list):
            update.message.reply_text('Invalid index. Please provide a valid image index.')
            return
        image_list.pop(index)
        update.message.reply_text(f'Image removed! Total images: {len(image_list)}')
    except ValueError:
        update.message.reply_text('Please provide a valid integer index for the image to delete.')


# Function to show all available commands
def show_commands(update: Update, context: CallbackContext) -> None:
    """Handles the .cmd command, shows available commands."""
    commands = (
        ".add <name> - Add a name to the participant list (group game)\n"
        ".remove <name> - Remove a name from the participant list (group game)\n"
        ".winner - Draw a random winner from the participant list\n"
        ".pic - Send a photo in direct message to add to the image list\n"
        ".delete <index> - Delete an image from the image list by index\n"
        ".cmd - Show available commands"
    )
    update.message.reply_text(commands)


# Function to ignore non-text messages (like photos, videos, etc.) in the group
def ignore_non_text_messages(update: Update, context: CallbackContext) -> None:
    """Ignores non-text messages (images, videos, voice, etc.)."""
    pass


def main():
    """Start the bot."""
    if not BOT_TOKEN:
        raise ValueError("No BOT_TOKEN found in environment variables.")
    if not GROUP_ID:
        raise ValueError("No GROUP_ID found in environment variables.")
    
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    # Command handlers for group game and image list management
    dispatcher.add_handler(CommandHandler("add", add_participant))
    dispatcher.add_handler(CommandHandler("remove", remove_participant))
    dispatcher.add_handler(CommandHandler("winner", announce_winner))
    dispatcher.add_handler(CommandHandler("cmd", show_commands))
    dispatcher.add_handler(CommandHandler("delete", delete_image))
    dispatcher.add_handler(CommandHandler("images", display_images_group))  # To display the images

    # Command handlers for image management via direct message
    dispatcher.add_handler(MessageHandler(filters.PHOTO, add_image))  # Handles images

    # Fallback handler for invalid commands
    dispatcher.add_handler(CommandHandler('.*', handle_invalid_command))

    # MessageHandler to ignore non-text messages (voice, video, image, etc.)
    dispatcher.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, ignore_non_text_messages))

    # Start polling for updates
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
