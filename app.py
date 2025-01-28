from flask import Flask, request
import requests
import random
import logging
import os

app = Flask(__name__)

participants = []

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
WHAPI_TOKEN = os.getenv('WHAPI_TOKEN')
WHATSAPP_GROUP_ID = os.getenv('WHATSAPP_GROUP_ID')  # Replace with your environment variable

@app.route("/", methods=['GET'])
def home():
    return "WhatsApp bot is running!"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    media_type = request.values.get('MediaContentType0', '')
    from_number = request.values.get('From', '')

    logger.info(f"Received message from {from_number}: {incoming_msg} with media type: {media_type}")

    if media_type in ['audio/ogg', 'image/jpeg', 'image/png', 'image/gif']:
        # Skip processing for voice messages and images, deliver directly to the group
        deliver_to_group("Media message received.")
    elif incoming_msg.lower().startswith('.add '):
        name = incoming_msg[5:].strip()
        logger.info(f"Received .add command with name: {name}")
        if len(participants) >= 20:
            deliver_to_group("The participant list is complete. Try again in the next game!")
        elif is_name_valid(name):
            add_participant(name, from_number)
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

    return "OK"

def is_name_valid(name):
    return name.replace(" ", "").isalpha()

def deliver_to_group(message):
    url = f'https://graph.facebook.com/v13.0/{WHATSAPP_GROUP_ID}/messages'
    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'group',
        'to': WHATSAPP_GROUP_ID,
        'type': 'text',
        'text': {
            'body': message
        }
    }
    headers = {
        'Authorization': f'Bearer {WHAPI_TOKEN}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(f"Failed to deliver message to group: {err.response.status_code} {err.response.reason}")
    except Exception as e:
        logger.error(f"Failed to deliver message to group: {e}")

def send_rules_message():
    message = ("Please check the group description or the pinned message for the rules.\n"
               "If you need further assistance, please DM the admin.")
    deliver_to_group(message)

def notify_incomplete_list():
    message = "The participant list is not yet complete. Please wait until we have 20 names."
    deliver_to_group(message)

def add_participant(name, phone_number):
    if len(participants) < 20:
        participants.append({'name': name, 'phone_number': phone_number})
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
