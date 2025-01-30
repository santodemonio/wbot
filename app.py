from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random
import logging
import os

app = Flask(__name__)

participants = []

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'your_default_bot_token')  # Add your Telegram bot token as an environment variable
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID', 'your_default_group_id')     # Add your Telegram group chat ID as an environment variable

bot = Bot(token=TELEGRAM_TOKEN)

@app.route("/", methods=['GET'])
def home():
    return "Telegram bot is running!"

@app.route("/telegram", methods=['POST'])
def telegram_bot():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

def is_name_valid(name):
    return name.replace(" ", "").isalpha()

def deliver_to_group(message):
    try:
        bot.send_message(chat_id=GROUP_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Failed to deliver message: {e}")

def send_rules_message():
    message = ("Please check the group description or the pinned message for the rules.\n"
               "If you need further assistance, please DM the admin.")
    deliver_to_group(message)

def notify_incomplete_list():
    message = "The participant list is not yet complete. Please wait until we have 20 names."
    deliver_to_group(message)

def add_participant(name, username):
    if len(participants) < 20:
        participants.append({'name': name, 'username': username})
        display_list()  # Logs the current list for debugging
        send_participant_list()  # Sends the updated list to the group

def display_list():
    list_str = "\n".join([p['name'] for p in participants])
    logger.info(f"Current List:\n{list_str}")

def get_participant_list():
    return "\n".join([p['name'] for p in participants])

def send_participant_list():
    list_str = get_participant_list()
    message = f"Current Participant List:\n{list_str}"
    deliver_to_group(message)

def select_winner():
    if participants:
        winner = random.choice(participants)
        announce_winner(winner)

def announce_winner(winner):
    list_str = "\n".join([f"**{p['name']}**" if p['name'] == winner['name'] else p['name'] for p in participants])
    message = (f"🎉🎊 *Congratulations!* 🎊🎉\n\n"
               f"✨ The winner is: **{winner['name']}** ✨\n\n"
               f"Please provide your Name, Address, and Phone Number for the prize delivery! 🏆🎁\n\n"
               f"Here is the list of all participants:\n\n{list_str}")
    logger.info(f"The winner announcement:\n{message}")
    deliver_to_group(message)

def clear_participants():
    participants.clear()
    logger.info("Participant list cleared for the new game.")

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your bot. Type .add <name> to participate.")

def handle_message(update: Update, context: CallbackContext):
    incoming_msg = update.message.text.strip()
    username = update.message.from_user.username

    if incoming_msg.lower().startswith('.add '):
        name = incoming_msg[5:].strip()
        if len(participants) >= 20:
            deliver_to_group("The participant list is complete. Try again in the next game!")
        elif is_name_valid(name):
            add_participant(name, username)
            send_participant_list()
            deliver_to_group(f"{name} has been added to the list. The current participant list has been sent to the group.")
        else:
            send_rules_message()
            deliver_to_group("Invalid name. Please check the group description or the pinned message for the rules.")
    elif incoming_msg.lower() == '.winner':
        if len(participants) == 20:
            select_winner()
            clear_participants()  # Clear the participant list for the new game
        else:
            notify_incomplete_list()
            deliver_to_group("The participant list is not yet complete. Please wait until we have 20 names.")
    else:
        send_rules_message()
        deliver_to_group("Invalid command. Please check the group description or the pinned message for the rules.")

# Set up the Updater and Dispatcher
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add handlers to the dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot
updater.start_polling()

if __name__ == "__main__":
    # Hardcode the port number directly
    app.run(host='0.0.0.0', port=5000)
