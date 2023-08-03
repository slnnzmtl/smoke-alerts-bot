import sys
sys.path.append('..')

import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from response import response
from subscribers import load_subscribers, add_subscriber, remove_subscriber, set_confidence
from alerts import handle_alert_verification
from cameras import check_camera_status
import re 

load_dotenv()

bot_token = os.environ.get('BOT_TOKEN')

max_confidence = 1
min_confidence = 0

def start(update, context):
    user_id = update.effective_user.id
    chat_id = update.message.chat_id
    subscribers = load_subscribers()

    if not any(subscriber['user_id'] == user_id for subscriber in subscribers):
        add_subscriber(user_id, chat_id)
        update.message.reply_text("You are now subscribed to smoke alerts.")
    else:
        update.message.reply_text("You already subscribed.")

def stop(update, context):
    user_id = update.effective_user.id

    remove_subscriber(user_id)
    update.message.reply_text("You are now unsubscribed from smoke alerts.")

def handle_confidence(update, context):
    chat_id = update.message.chat_id
    text = update.message.text

    if (text == '/confidence'):
        update.message.reply_text("Enter a new confidence level")
        return

    pattern = r'-?\d+(\.\d+)?\*?'
    match = re.search(pattern, text)
    value = float(match.group())

    if (value < 0 or value > 1):
        update.message.reply_text("Confidence should be in the range from 0 to 1.")
    else:
        set_confidence(chat_id, value)

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("confidence", handle_confidence))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_confidence))

    dp.add_handler(CallbackQueryHandler(handle_alert_verification))

    job_queue = updater.job_queue
    job_queue.run_repeating(check_camera_status, interval=30, first=1)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
