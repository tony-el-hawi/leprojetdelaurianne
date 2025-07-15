from flask_restx import fields

item_model_def = {
    'id': fields.String(description="Identifiant unique de l'article"),
    'name': fields.String(example="Nom", description="Nom de l'article"),
    'category': fields.String(example="Chemises", description="Catégorie de l'article"),
    'color': fields.String(example="Bleu", description="Couleur de l'article"),
    'size': fields.String(example="L", description="Taille de l'article"),
    'photo': fields.String(example="data:image/webp;base64,...", description="Photo encodée en base64"),
    'tag_id': fields.String(example="Identifiant NFC/RFID", description="Identifiant du tag NFC/RFID"),
    'hanger_id': fields.String(example="cintre-uuid", description="Identifiant du cintre associé (unique, nullable)")
}


item_model_db_init = '''CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        color TEXT,
        size TEXT,
        photo TEXT,
        tag_id TEXT,
        hanger_id TEXT UNIQUE
    )'''

order_model_def = {
    'id': fields.String,
    'items': fields.List(fields.Raw, example=[{ "id": "d49f25b2-865b-4368-8e45-9ca486914eaa",
    "name": "Short denim clair",
    "category": "Shorts",
    "color": "Bleu clair",
    "size": "34",
    "photo": "/photos/d49f25b2-865b-4368-8e45-9ca486914eaa.jpeg"}]),
    'timestamp': fields.String,
    'status': fields.String
}

order_model_db_init = '''CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        status TEXT,
        items TEXT
    )'''


hanger_model_def = {
    'id': fields.String,
    'tag_id': fields.String(example="Identifiant NFC/RFID", description="Identifiant du tag NFC/RFID du cintre"),
    'mqtt_topic': fields.String(example="topic/cintre/123", description="Nom du topic MQTT associé au cintre")
}

hanger_model_db_init = '''CREATE TABLE IF NOT EXISTS hangers (
    id TEXT PRIMARY KEY,
    tag_id TEXT NOT NULL,
    mqtt_topic TEXT NOT NULL
)'''
