import json
import os
from dotenv import load_dotenv
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, MessageHandler

load_dotenv()

bot_token = os.environ.get('BOT_TOKEN')
api_endpoint = os.environ.get('API_ENDPOINT')

subscribed_users = {}

def start(update, context):
    user_id = update.effective_user.id
    if user_id not in subscribed_users:
        subscribed_users[user_id] = update.message.chat_id
        update.message.reply_text("You are now subscribed to smoke alerts.")

def stop(update, context):
    user_id = update.effective_user.id
    if user_id in subscribed_users:
        del subscribed_users[user_id]
        update.message.reply_text("You are now unsubscribed from smoke alerts.")

def check_smoke_status(context):
    response = requests.get(api_endpoint)
    data = response.json()

    for camera in data:
        if camera['smoke_detected']:
            for user_id, chat_id in subscribed_users.items():
                name = camera['camera_name']
                address = camera['camera_address']
                img_url = camera['image']
                smoke_detected = camera['smoke_detected']
                confidence = camera['confidence']

                callback_success = json.dumps({'s': True, 'c': confidence})
                callback_error = json.dumps({'s': False, 'c': confidence})

                keyboard = [[
                    InlineKeyboardButton("👍", callback_data=callback_success), 
                    InlineKeyboardButton("👎", callback_data=callback_error)
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                context
                context.bot.send_message(chat_id=chat_id, text=f"{name}\n{address}\n{confidence}\n{smoke_detected}", reply_markup=reply_markup)

def handle_button_press(update, context):
    query = update.callback_query
    data = json.loads(query.data)
    chat_id = query.message.chat_id
    status = data.get('s')
    confidence = data.get('c')

    if status == True:
        context.bot.send_message(chat_id=chat_id, text=f"Good! Confidence {confidence}")
    else:
        context.bot.send_message(chat_id=chat_id, text=f"Bad! Confidence {confidence}")

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CallbackQueryHandler(handle_button_press))

    job_queue = updater.job_queue
    job_queue.run_repeating(check_smoke_status, interval=10, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
