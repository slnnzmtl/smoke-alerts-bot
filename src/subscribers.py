import sys
sys.path.append('..')

import json
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

db_path = os.environ.get('DATABASE_PATH')
default_confidence = os.environ.get('DEFAULT_CONFIDENCE')

def load_subscribers():
    try:
        with open(f"../{db_path}", 'r') as file:
            data = json.load(file)
            return data['subscribers']
    except FileNotFoundError:
        return []
    
def save_subscribers(subscribers):
    data = {'subscribers': subscribers}
    with open(f"../{db_path}", 'w') as file:
        json.dump(data, file, indent=4)

def add_subscriber(user_id, chat_id, username):
    current_time = datetime.datetime.now()
    subscribed_on = current_time.strftime("%Y-%m-%d %H:%M:%S")
    subscribers = load_subscribers()
    subscribers.append({ 
        "user_id": user_id,
        "chat_id": chat_id, 
        "username": username,
        "subscribed_on": subscribed_on, 
        "confidence": default_confidence 
    })

    save_subscribers(subscribers)

def remove_subscriber(user_id): 
    subscribers = load_subscribers()
    subscribers = [subscriber for subscriber in subscribers if subscriber['user_id'] != user_id]
    save_subscribers(subscribers)

def set_confidence(user_id, confidence):
    subscribers = load_subscribers()
    new_subscribers = []

    for subscriber in subscribers:
        if subscriber['user_id'] == user_id:
            updated_subscriber = { **subscriber, 'confidence': confidence }
            new_subscribers.append(updated_subscriber)
        else:
            new_subscribers.append(subscriber)
        
    save_subscribers(new_subscribers)
    