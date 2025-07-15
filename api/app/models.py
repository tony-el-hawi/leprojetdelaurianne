from flask_restx import fields

item_model_def = {
    'id': fields.String,
    'name': fields.String(example="Nom"),
    'category': fields.String(example="Chemises"),
    'color': fields.String(example="Bleu"),
    'size': fields.String(example="L"),
    'photo': fields.String(example="data:image/webp;base64,...")
}

item_model_db_init = '''CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        color TEXT,
        size TEXT,
        photo TEXT
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