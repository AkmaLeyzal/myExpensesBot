import sys
import logging
import traceback

import telebot
from flask import Flask, request, abort

import config
from bot import bot

app = Flask(__name__)

bot.threaded = False

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WebhookExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        logger.error(f"Bot handler error: {exception}")
        logger.error(traceback.format_exc())
        return True


bot.exception_handler = WebhookExceptionHandler()


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("UTF-8")
        logger.info("Webhook received update")
        try:
            update = telebot.types.Update.de_json(json_str)
            bot.process_new_updates([update])
            logger.info("Update processed successfully")
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            logger.error(traceback.format_exc())
        return "", 200
    else:
        abort(403)


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    bot.remove_webhook()
    success = bot.set_webhook(url=config.WEBHOOK_URL)
    if success:
        return f"Webhook set to: {config.WEBHOOK_URL}", 200
    else:
        return "Failed to set webhook", 500


@app.route("/remove_webhook", methods=["GET"])
def remove_webhook():
    bot.remove_webhook()
    return "Webhook removed.", 200


@app.route("/", methods=["GET"])
def index():
    return "Expense Tracker Bot is running!", 200