from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import random
import logging

app = Flask(__name__)

# Twilio credentials (use environment variables for security)
account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
client = Client(account_sid, auth_token)

participants = []

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=['GET'])
def home():
    return "WhatsApp bot is running!"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    if incoming_msg.lower().startswith('.add '):
        name = incoming_msg[5:].strip()  # Extract the name after the ".add " command
        if is_name_valid(name):
            add_participant(name, from_number)
        else:
            send_rules_message(from_number)
    elif incoming_msg.lower() == '.winner':
        if len(participants) == 20:
            select_winner()
        else:
            notify_incomplete_list(from_number)
    else:
        send_rules_message(from_number)

    return str(MessagingResponse())

def is_name_valid(name):
    # Check if the name contains only alphabetic characters and spaces
    return name.replace(" ", "").isalpha()

def send_rules_message(phone_number):
    message = ("Please check the group description or the pinned message for the rules.\n"
               "If you need further assistance, please DM the admin.")

    client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
        to=phone_number
    )

def notify_incomplete_list(phone_number):
    message = "The participant list is not yet complete. Please wait until we have 20 names."

    client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
        to=phone_number
    )

def add_participant(name, phone_number):
    if len(participants) < 20:
        participants.append({'name': name, 'phone_number': phone_number})
        display_list()

def display_list():
    list_str = "\n".join([p['name'] for p in participants])
    # Log the current list to the console for debugging
    logger.info(f"Current List:\n{list_str}")

def select_winner():
    if participants:
        winner = random.choice(participants)
        # Make the winner announcement look cool
        announce_winner(winner)

def announce_winner(winner):
    # Create a cool looking announcement message
    message = (f"🎉🎊 *Congratulations!* 🎊🎉\n\n"
               f"✨ The winner is: *{winner['name']}* ✨\n\n"
               f"Please provide your Name, Address, and Phone Number for the prize delivery! 🏆🎁")

    # Log the winner announcement to the console for debugging
    logger.info(f"The winner announcement:\n{message}")

    # Send the cool looking winner announcement to the WhatsApp group
    group_phone_number = 'whatsapp:+14155238886'  # Replace with your Twilio WhatsApp group number
    client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
        to=group_phone_number
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


