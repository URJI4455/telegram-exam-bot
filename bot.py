import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request
import asyncio

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Create Telegram app
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Simple command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot is online on Railway!")

# Add command
telegram_app.add_handler(CommandHandler("start", start))

# Webhook for Railway
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return 'ok'

# Home page
@app.route('/')
def home():
    return "✅ Telegram Bot Running on Railway!"

# Initialize bot
async def init_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    print("🤖 Bot initialized!")

# Run the app
if __name__ == "__main__":
    # Initialize bot
    asyncio.run(init_bot())
    
    # Start Flask
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)