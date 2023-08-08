import os
import requests
from subscribers import load_subscribers
from alerts import send_alert, get_pushed_alert
from dotenv import load_dotenv
import json
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

api_endpoint = os.environ.get('API_ENDPOINT')
camera_list_path = os.environ.get('CAMERA_LIST_PATH')

with open(camera_list_path, 'r') as json_file:
    camera_list = json.load(json_file)

def fetch_cameras(cameras):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)

    camera_data = []

    for camera in cameras:
        camera_address = camera['address']

        path = f"{api_endpoint}?camera_address={camera_address}"
        try:
            response = session.get(path)
            response.raise_for_status()
            json_data = response.json()
            camera_data = json_data
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            continue
        except Exception as e:
            print(e)
            continue

    return camera_data

def check_camera_status(context):
    subscribers = load_subscribers()
    cameras = fetch_cameras(camera_list)
    
    for camera in cameras: 
        camera['camera_name']
        if camera['smoke_detected']:
            address = camera['camera_address']
            confidence = camera['confidence']

            for subscriber in subscribers:
                chat_id = subscriber['chat_id']
                min_confidence = float(subscriber['confidence'])
                
                alert = get_pushed_alert(chat_id, address)
                is_alert_checked = alert.get('confidence') == confidence

                if not is_alert_checked:
                    if (confidence > min_confidence):
                        send_alert(context, chat_id, camera)
