import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
    WEBAPP_HOST = os.getenv('WEBAPP_HOST')
    WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', 8000))

    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
