import sys
sys.path.append('..')

import json
import base64
import os
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

log_directory = '../database/alerts_log/'
pushed_alerts = {}

def save_image(output_directory, alert):
    confidence = alert['confidence']
    image_string = alert['image']
    filename = f"{confidence}.jpg"
    
    image_data = base64.b64decode(image_string)

    output_path = os.path.join(output_directory, filename)
    with open(output_path, 'wb') as image_file:
        image_file.write(image_data)

def approve_alert(alert):
    output_directory = f"{log_directory}/approved"
    save_image(output_directory, alert)


def reject_alert(alert):
    output_directory = f"{log_directory}/rejected"
    save_image(output_directory, alert)

def handle_alert_verification(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = json.loads(query.data)

    approved = 't' in data
    camera_name = data.get('t') if approved else data.get('f')

    alert = get_pushed_alert(chat_id, camera_name)

    if approved: 
        approve_alert(alert)
    else:
        reject_alert(alert)

    
def send_alert(context, chat_id, camera):
    name = camera['camera_name']
    address = camera['camera_address']
    confidence = camera['confidence']
    image = base64.b64decode(camera.get('image', ''))

    callback_success = json.dumps({ "t": address })
    callback_failure = json.dumps({ "f": address })

    keyboard = [[
        InlineKeyboardButton("👍", callback_data=callback_success), 
        InlineKeyboardButton("👎", callback_data=callback_failure), 
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if (image):
        context.bot.send_photo(
            chat_id=chat_id,
            photo=BytesIO(image),
            caption=f'{name}\nConfidence: {confidence}', 
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'{name}\nConfidence: {confidence}',
            reply_markup=reply_markup
        )

    if chat_id not in pushed_alerts:
        pushed_alerts[chat_id] = {}
    
    pushed_alerts[chat_id][address] = camera

def get_pushed_alert(chat_id, address):
    chat = pushed_alerts.get(chat_id, {})
    alert = chat.get(address, {})

    return alert


