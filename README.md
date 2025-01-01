# Smart Grocery Manager Bot

A Telegram bot that helps users track their groceries, expiration dates, and provides smart shopping suggestions.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file with your Telegram Bot Token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
MONGODB_URI=your_mongodb_uri_here
```

4. Run the bot:
```bash
python src/main.py
```

## Getting a Telegram Bot Token

1. Open Telegram and search for "@BotFather"
2. Start a chat with BotFather
3. Send "/newbot" command
4. Follow instructions to name your bot
5. Save the API token provided by BotFather

## Features

- Scan receipts and barcodes
- Track grocery expiration dates
- Get spending analytics
- Receive smart notifications
- Generate shopping lists

## Project Structure

```
├── src/
│   ├── main.py           # Main bot file
│   ├── config.py         # Configuration settings
│   ├── handlers/         # Command handlers
│   ├── database/         # Database operations
│   └── utils/           # Helper functions
├── requirements.txt
├── README.md
└── .env                 # Environment variables (not in git)
```
