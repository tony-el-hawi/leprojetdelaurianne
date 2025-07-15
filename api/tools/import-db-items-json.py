import json
import requests

API_URL = "http://localhost:5000/items"

with open("db-items-history.json", "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    # On retire la clé 'mock' si présente, car l'API ne la gère pas
    item.pop('mock', None)
    response = requests.post(API_URL, json=item)
    print(f"Ajout de {item.get('name')}: {response.status_code} - {response.text}")