import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request

# Enable basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Global variable for the Telegram application
telegram_app = None

# --- Telegram Bot Logic ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text("🚀 Bot is online on Railway!")

def setup_telegram_app():
    """Initialize the Telegram Application."""
    global telegram_app
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN environment variable is not set!")
        # Don't raise an error here, let Flask start so you can see the error page
        return

    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    logger.info("🤖 Telegram application object created (awaiting initialization).")

# --- Flask Routes ---
@app.route('/')
def home():
    return "✅ Telegram Bot Running on Railway! Webhook path is at /webhook"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint where Telegram sends updates."""
    global telegram_app
    if telegram_app is None:
        return "Bot not initialized", 500

    try:
        # 1. Get the update from Telegram's request
        json_str = request.get_data().decode('utf-8')
        update = Update.de_json(json_str, telegram_app.bot)

        # 2. Create a new event loop to run the async update processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.process_update(update))
        return 'ok'
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'error', 500

# --- Application Factory & Run ---
# This runs BEFORE the Flask server starts
@app.before_first_request
def initialize_bot():
    """Initialize the bot before the first request (legacy method for clarity)."""
    if telegram_app is None:
        setup_telegram_app()
        if telegram_app:
            # Initialize the bot application (sets up internal queues)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(telegram_app.initialize())
            loop.run_until_complete(telegram_app.start())
            logger.info("✅ Bot initialized and started.")

# Run the Flask app (this is the blocking call that keeps the process alive)
if __name__ == "__main__":
    # Initial setup: create the app object
    setup_telegram_app()
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)