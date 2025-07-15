import json
import requests

API_URL_ORDERS = "http://localhost:5000/orders"

with open("db-orders-history.json", "r", encoding="utf-8") as f:
    orders = json.load(f)

for order in orders:
    order.pop('mock', None)
    response = requests.post(API_URL_ORDERS, json=order)
    print(f"Ajout de {order.get('name', order.get('id', 'order'))}: {response.status_code} - {response.text}")