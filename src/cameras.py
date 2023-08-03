import os
import requests
from subscribers import load_subscribers
from alerts import send_alert, get_pushed_alert
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv

load_dotenv()

api_endpoint = os.environ.get('API_ENDPOINT')

def check_camera_status(context):
    response = requests.get(api_endpoint)
    data = response.json() 
    subscribers = load_subscribers()

    for camera in data:
        if camera['smoke_detected']:
            address = camera['camera_address']
            confidence = camera['confidence']

            for subscriber in subscribers:
                chat_id = subscriber['chat_id']
                min_confidence = subscriber['confidence']
                
                alert = get_pushed_alert(chat_id, address)
                is_alert_checked = alert.get('confidence') == confidence

                if not is_alert_checked:
                    if (confidence > min_confidence):
                        send_alert(context, chat_id, camera)

