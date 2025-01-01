import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in .env file")

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = 'grocery_manager'

# Message templates
WELCOME_MESSAGE = """
Welcome to Smart Grocery Manager! 🛒

I can help you:
📸 Scan receipts and barcodes
📅 Track expiration dates
💰 Monitor your spending
🔔 Send you notifications
📝 Create shopping lists

Use /help to see all available commands!
"""

HELP_MESSAGE = """
Available commands:

/start - Start the bot
/scan - Scan a receipt or barcode
/list - View your grocery list
/stats - View your spending statistics
/expire - Check expiring items
/help - Show this help message

Send me a photo of your receipt or barcode to add items!
"""
