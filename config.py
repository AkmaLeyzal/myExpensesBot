import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, "credential.env"))

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_FILE = os.path.join(BASE_DIR, os.getenv("GOOGLE_CREDS_FILE", "rapid-spider-466710-u6-7a35f1f445fe.json"))
PYTHONANYWHERE_USERNAME = os.getenv("PYTHONANYWHERE_USERNAME", "akmaleyzal")

WEBHOOK_URL = f"https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com/webhook"

_required = {
    "BOT_API_TOKEN": BOT_API_TOKEN,
    "SPREADSHEET_ID": SPREADSHEET_ID,
}
for key, value in _required.items():
    if not value:
        raise ValueError(f"Missing required config: {key}. Please set it in credential.env")
