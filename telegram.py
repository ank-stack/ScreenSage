import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_API")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    message = message.strip()
    if not message:
        return None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    resp.raise_for_status()
    return resp.json()["result"]["message_id"]