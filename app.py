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

    logger.info(f"Received message from {from_number}: {incoming_msg}")
    resp = MessagingResponse()

    if incoming_msg.lower().startswith('.add '):
        name = incoming_msg[5:].strip()  # Extract the name after the ".add " command
        logger.info(f"Received .add command with name: {name}")
        if is_name_valid(name):
            add_participant(name, from_number)
            try:
                send_participant_list()
                resp.message(f"{name} has been added to the list. The current participant list has been sent to the group.")
            except Exception as e:
                logger.error(f"Failed to send participant list: {e}")
                resp.message(f"{name} has been added to the list, but there was an error sending the current participant list to the group.")
        else:
            send_rules_message(from_number)
            resp.message("Invalid name. Please check the group description or the pinned message for the rules.")
    elif incoming_msg.lower() == '.winner':
        if len(participants) == 20:
            select_winner()
            resp.message("The winner has been announced in the group!")
        else:
            notify_incomplete_list(from_number)
            resp.message("The participant list is not yet complete. Please wait until we have 20 names.")
    else:
        send_rules_message(from_number)
        resp.message("Invalid command. Please check the group description or the pinned message for the rules.")

    logger.info(f"Sending response: {str(resp)}")
    return str(resp)

def is_name_valid(name):
    # Check if the name contains only alphabetic characters and spaces
    return name.replace(" ", "").isalpha()

def send_rules_message(phone_number):
    message = ("Please check the group description or the pinned message for the rules.\n"
               "If you need further assistance, please DM the admin.")

    try:
        client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
            to=phone_number
        )
    except Exception as e:
        logger.error(f"Failed to send rules message: {e}")

def notify_incomplete_list(phone_number):
    message = "The participant list is not yet complete. Please wait until we have 20 names."

    try:
        client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
            to=phone_number
        )
    except Exception as e:
        logger.error(f"Failed to send incomplete list notification: {e}")

def add_participant(name, phone_number):
    if len(participants) < 20:
        participants.append({'name': name, 'phone_number': phone_number})
        display_list()

def display_list():
    list_str = "\n".join([p['name'] for p in participants])
    logger.info(f"Current List:\n{list_str}")

def get_participant_list():
    return "\n".join([p['name'] for p in participants])

def send_participant_list():
    list_str = get_participant_list()
    message = f"Current Participant List:\n{list_str}"
    
    twilio_whatsapp_number = 'whatsapp:+14155238886'  # Your Twilio WhatsApp number
    try:
        client.messages.create(
            body=message,
            from_=twilio_whatsapp_number,  # Use your Twilio WhatsApp number as the sender
            to='whatsapp:+<Your Personal WhatsApp Number>'  # Send the message to the group using a participant number
        )
    except Exception as e:
        logger.error(f"Failed to send participant list: {e}")

def select_winner():
    if participants:
        winner = random.choice(participants)
        announce_winner(winner)

def announce_winner(winner):
    message = (f"🎉🎊 *Congratulations!* 🎊🎉\n\n"
               f"✨ The winner is: *{winner['name']}* ✨\n\n"
               f"Please provide your Name, Address, and Phone Number for the prize delivery! 🏆🎁")

    logger.info(f"The winner announcement:\n{message}")

    twilio_whatsapp_number = 'whatsapp:+14155238886'  # Your Twilio WhatsApp number
    try:
        client.messages.create(
            body=message,
            from_=twilio_whatsapp_number,  # Use your Twilio WhatsApp number as the sender
            to='whatsapp:+<917560885958'  # Send the message to the group using a participant number
        )
    except Exception as e:
        logger.error(f"Failed to send winner announcement: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)




