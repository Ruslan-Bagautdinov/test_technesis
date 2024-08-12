from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
