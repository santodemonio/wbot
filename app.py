import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

name_list = []
MAX_NAMES = 20

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

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("winner", winner))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))
    
    print("Bot is running...")
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
