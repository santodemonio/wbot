import os
import random
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
WEBHOOK_URL = f"https://wbot.onrender.com/webhook"  # Webhook URL using app name

name_list = []
MAX_NAMES = 20

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Telegram bot application
app = Application.builder().token(TOKEN).build()

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: .add <your name>")
        return
    
    name = context.args[0].strip().capitalize()
    if len(name_list) >= MAX_NAMES:
        await update.message.reply_text("List is full! Try next game.")
        return
    
    if name in name_list:
        await update.message.reply_text("You have already added your name!")
        return
    
    name_list.append(name)
    list_message = "\n".join([f"{i+1}. {n}" for i, n in enumerate(name_list)])
    await update.message.reply_text(f"Updated List:\n{list_message}")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: .remove <your name>")
        return
    
    name = context.args[0].strip().capitalize()
    if name in name_list:
        name_list.remove(name)
        await update.message.reply_text(f"{name} has been removed from the list.")
    else:
        await update.message.reply_text("Name not found in the list.")

async def winner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(name_list) < MAX_NAMES:
        await update.message.reply_text("The list is not full yet! Keep adding names.")
        return
    
    winner = random.choice(name_list)
    await update.message.reply_text(f"🎉🎊 Congratulations {winner}! 🎊🎉\n\nPlease provide your Name, Address, and Phone Number.")
    
    name_list.clear()
    await update.message.reply_text("The list has been reset. Start adding names for the next game!")

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("Check the pinned message or DM the admin.")
    else:
        await update.message.delete()

# Telegram Webhook Route
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    """Receives updates from Telegram and processes them."""
    update = Update.de_json(request.get_json(), app.bot)
    app.update_queue.put_nowait(update)
    return "OK", 200

@flask_app.route("/")
def home():
    """Health check route for Render."""
    return "Telegram Bot is Running with Webhook!", 200

async def set_webhook():
    """Sets the webhook URL for Telegram."""
    await app.bot.set_webhook(WEBHOOK_URL)

def main():
    """Starts the Flask server and sets up the Telegram Webhook."""
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("winner", winner))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    # Set webhook when bot starts
    asyncio.run(set_webhook())

    # Run Flask server
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  # Auto-detect Render port

if __name__ == "__main__":
    main()
