from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from PIL import Image, ImageDraw, ImageFont
import random

app = Flask(__name__)

# Twilio credentials (use environment variables for security)
account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
client = Client(account_sid, auth_token)

names_list = []
group_members = ['whatsapp:+1234567890', 'whatsapp:+0987654321']  # Add your group members' numbers here

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    if incoming_msg.lower() == 'done':
        return str(MessagingResponse())

    add_name_and_update_list(incoming_msg, from_number)
    return str(MessagingResponse())

def add_name_and_update_list(name, from_number):
    if len(names_list) < 20:
        names_list.append(name)
        display_list(from_number)
        if len(names_list) == 20:
            select_winner()

def display_list(from_number):
    list_str = "\n".join(names_list)
    create_and_send_image(f"Current List:\n{list_str}", from_number)

def select_winner():
    if names_list:
        winner = random.choice(names_list)
        announce_winner(winner)

def announce_winner(winner):
    message = f"🎉 The winner is: {winner} 🎉\nPlease provide your Name, Address, and Phone Number."
    for number in group_members:
        create_and_send_image(message, number)

def create_and_send_image(text, to):
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 24)
    draw.text((10, 10), text, fill='black', font=font)
    img_path = "output_image.png"
    img.save(img_path)
    
    static_url = f'https://your-static-url-on-render.com/{img_path}'
    
    client.messages.create(
        media_url=[static_url],
        from_='whatsapp:+14155238886',
        to=to
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

