# zoom_utils.py
import requests
from base64 import b64encode

CLIENT_ID = "X9Oz713ZTCqX6wzEPk8NQg"
CLIENT_SECRET = "ydp6MfJZLCGBQbW10gibfj2rEdZA4PtB"
ACCOUNT_ID = "1JQYGMKuTPCjSrGx3hEUKA"

def get_zoom_access_token():
    credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    params = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(url, headers=headers, params=params)
    return response.json().get("access_token")

def create_zoom_meeting(access_token, topic, start_time):
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        "type": 2,
        "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "duration": 60,
        "timezone": "Asia/Kolkata",
        "settings": {
            "join_before_host": True
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 201:
        print("Zoom API error:", response.status_code, response.text)
        return {}  # return empty dict if error
    return response.json()