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
WHAPI_SID = os.getenv('WHAPI_SID')
WHATSAPP_GROUP_ID = 'BAZGp6Be0dy0Czl4xqygfV'  # Your provided Group ID

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
        resp_msg = "Media message received and delivered to the group."
    elif incoming_msg.lower().startswith('.add '):
        name = incoming_msg[5:].strip()
        logger.info(f"Received .add command with name: {name}")
        if len(participants) >= 20:
            resp_msg = "The participant list is complete. Try again in the next game!"
            deliver_to_group(resp_msg)
        elif is_name_valid(name):
            add_participant(name, from_number)
            try:
                send_participant_list()
                resp_msg = f"{name} has been added to the list. The current participant list has been sent to the group."
            except Exception as e:
                logger.error(f"Failed to send participant list: {e}")
                resp_msg = f"{name} has been added to the list, but there was an error sending the current participant list to the group."
            deliver_to_group(resp_msg)
        else:
            send_rules_message(from_number)
            resp_msg = "Invalid name. Please check the group description or the pinned message for the rules."
            deliver_to_group(resp_msg)
    elif incoming_msg.lower() == '.winner':
        if len(participants) == 20:
            select_winner()
            resp_msg = "The winner has been announced in the group!"
        else:
            notify_incomplete_list(from_number)
            resp_msg = "The participant list is not yet complete. Please wait until we have 20 names."
        deliver_to_group(resp_msg)
    else:
        send_rules_message(from_number)
        resp_msg = "Invalid command. Please check the group description or the pinned message for the rules."
        deliver_to_group(resp_msg)

    logger.info(f"Sending response: {resp_msg}")
    return resp_msg

def is_name_valid(name):
    return name.replace(" ", "").isalpha()

def deliver_to_group(message):
    url = 'https://gate.whapi.cloud/messages/text'  # Updated URL
    payload = {
        'to': WHATSAPP_GROUP_ID,  # Send the message to the group using the Group ID
        'body': message  # Updated key to 'body' as per the example
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'authorization': f'Bearer {WHAPI_TOKEN}'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(f"Failed to deliver message to group: {err.response.status_code} {err.response.reason}")
    except Exception as e:
        logger.error(f"Failed to deliver message to group: {e}")

def send_rules_message(phone_number):
    message = ("Please check the group description or the pinned message for the rules.\n"
               "If you need further assistance, please DM the admin.")

    deliver_to_group(message)

def notify_incomplete_list(phone_number):
    message = "The participant list is not yet complete. Please wait until we have 20 names."

    deliver_to_group(message)

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
    deliver_to_group(message)

def select_winner():
    if participants:
        winner = random.choice(participants)
        announce_winner(winner)

def announce_winner(winner):
    message = (f"🎉🎊 *Congratulations!* 🎊🎉\n\n"
               f"✨ The winner is: *{winner['name']}* ✨\n\n"
               f"Please provide your Name, Address, and Phone Number for the prize delivery! 🏆🎁")

    logger.info(f"The winner announcement:\n{message}")
    deliver_to_group(message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
