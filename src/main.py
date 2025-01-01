from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import logging
import sys
import os
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, WELCOME_MESSAGE, HELP_MESSAGE
from database import DatabaseManager
from utils.image_processor import ImageProcessor

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseManager()

# States for conversation handler
SCANNING = 1

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    db.add_user(user.id, user.username)
    await update.message.reply_text(WELCOME_MESSAGE)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    await update.message.reply_text(HELP_MESSAGE)

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /scan command."""
    await update.message.reply_text(
        "Please send me a photo of your receipt or barcode! 📸\n"
        "Make sure the image is clear and well-lit."
    )
    return SCANNING

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received photos."""
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    
    # Create temp directory if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    
    # Download the photo
    photo_path = f"temp/photo_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await photo_file.download_to_drive(photo_path)
    
    # Try processing as receipt first
    receipt_data = ImageProcessor.process_receipt(photo_path)
    
    if receipt_data and receipt_data.get('items'):
        # Successfully processed receipt
        response = "📝 Here's what I found in your receipt:\n\n"
        total = 0
        for item in receipt_data['items']:
            response += f"• {item['name']}: ${item['price']:.2f}\n"
            total += item['price']
            
            # Add to database
            db.add_product({
                'name': item['name'],
                'price': item['price'],
                'purchase_date': receipt_data.get('date', datetime.now()),
                'type': 'receipt_item'
            })
        
        response += f"\nTotal: ${total:.2f}"
        
    else:
        # Try processing as barcode
        barcode = ImageProcessor.process_barcode(photo_path)
        if barcode:
            response = f"Found barcode: {barcode}\n(Product lookup will be implemented soon!)"
        else:
            response = "Sorry, I couldn't process this image. Please make sure it's a clear photo of a receipt or barcode."
    
    # Clean up
    os.remove(photo_path)
    
    await update.message.reply_text(response)
    return ConversationHandler.END

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show spending statistics."""
    user = update.effective_user
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_spending = db.get_monthly_spending(user.id, current_month, current_year)
    
    response = f"📊 Your Statistics:\n\n"
    response += f"This month's spending: ${monthly_spending:.2f}\n"
    
    await update.message.reply_text(response)

def run_bot():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add conversation handler for scanning
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("scan", scan_command)],
        states={
            SCANNING: [MessageHandler(filters.PHOTO, handle_photo)]
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)

    # Start the Bot
    print("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        run_bot()
    except KeyboardInterrupt:
        print("Bot stopped by user")
        sys.exit(0)
