import json
import requests
import os
import base64

API_URL = "http://10.42.0.1:5080/hangers"

response = requests.get(API_URL)
response.raise_for_status()
hangers = response.json()

for hanger in hangers:
    hanger_id = hanger.get('id')
    if hanger_id is not None:
        delete_url = f"{API_URL}/{hanger_id}"
        del_response = requests.delete(delete_url)
        del_response.raise_for_status()
        print(f"Deleted hanger with id {hanger_id}")