from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from datetime import datetime
import uuid
import sqlite3
import json
import os

from models import item_model_def, item_model_db_init, order_model_def, order_model_db_init, hanger_model_def, hanger_model_db_init

# Dossier photos accessible en static
PHOTOS_DIR = os.path.join(os.path.dirname(__file__), '..', 'photos')
app = Flask(__name__, static_url_path='/photos', static_folder=PHOTOS_DIR)
CORS(app)
api = Api(app, title='Le Dressing de Laurianne API', description='API locale avec Swagger/OpenAPI', doc='/swagger/')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.sqlite3')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

item_model = api.model('Item', item_model_def)
order_model = api.model('Order', order_model_def)
hanger_model = api.model('Hanger', hanger_model_def)
tag_input_model = api.model('TagInput', {
    'tag_id': fields.String(example="Identifiant NFC/RFID", description="Identifiant du tag lu")
})

@api.route('/items')
class ItemList(Resource):
    @api.marshal_list_with(item_model)
    def get(self):
        """Récupère tous les items"""
        conn = get_db()
        cur = conn.execute('SELECT * FROM items')
        items = [dict(row) for row in cur.fetchall()]
        conn.close()
        return items, 200

    @api.expect(item_model)
    @api.marshal_with(item_model, code=201)
    def post(self):
        """Crée un nouvel item (supporte l'upload de photo en base64 ou lien direct)"""
        data = api.payload
        item_id = str(uuid.uuid4())
        photo_url = data.get('photo')
        tag_id = data.get('tag_id')
        hanger_id = data.get('hanger_id')

        # Si la photo est en base64, on la sauvegarde localement
        if photo_url and photo_url.startswith('data:image'):
            import base64
            header, encoded = photo_url.split(',', 1)
            ext = header.split('/')[1].split(';')[0]
            filename = f"{item_id}.{ext}"
            photo_path = os.path.join(os.path.dirname(__file__), '..', 'photos', filename)
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            with open(photo_path, 'wb') as f:
                f.write(base64.b64decode(encoded))
            # On stocke le lien local
            photo_url = f"/photos/{filename}"

        conn = get_db()
        conn.execute(
            'INSERT INTO items (id, name, category, color, size, photo, tag_id, hanger_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (item_id, data.get('name'), data.get('category'), data.get('color'), data.get('size'), photo_url, tag_id, hanger_id)
        )
        conn.commit()
        item = {
            'id': item_id,
            'name': data.get('name'),
            'category': data.get('category'),
            'color': data.get('color'),
            'size': data.get('size'),
            'photo': photo_url,
            'tag_id': tag_id,
            'hanger_id': hanger_id
        }
        conn.close()
        return item, 201


@api.route('/items/<string:id>')
class Item(Resource):
    @api.expect(item_model)
    def put(self, id):
        """Met à jour un item"""
        data = api.payload
        conn = get_db()
        cur = conn.execute('SELECT * FROM items WHERE id = ?', (id,))
        if cur.fetchone() is None:
            conn.close()
            return {'error': 'Item not found'}, 404
        conn.execute(
            'UPDATE items SET name = ?, category = ?, color = ?, size = ?, photo = ?, tag_id = ?, hanger_id = ? WHERE id = ?',
            (data.get('name'), data.get('category'), data.get('color'), data.get('size'), data.get('photo'), data.get('tag_id'), data.get('hanger_id'), id)
        )
        conn.commit()
        conn.close()
        return {'message': 'Item updated successfully'}, 200

    def delete(self, id):
        """Supprime un item"""
        conn = get_db()
        conn.execute('DELETE FROM items WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return {'message': 'Item deleted successfully'}, 200


@api.route('/hangers')
class HangerList(Resource):
    @api.marshal_list_with(hanger_model)
    def get(self):
        """Récupère tous les cintres"""
        conn = get_db()
        cur = conn.execute('SELECT * FROM hangers')
        hangers = [dict(row) for row in cur.fetchall()]
        conn.close()
        return hangers, 200

    @api.expect(hanger_model)
    @api.marshal_with(hanger_model, code=201)
    def post(self):
        """Crée un nouveau cintre"""
        data = api.payload
        hanger_id = str(uuid.uuid4())
        conn = get_db()
        conn.execute(
            'INSERT INTO hangers (id, tag_id, mqtt_topic) VALUES (?, ?, ?)',
            (hanger_id, data.get('tag_id'), data.get('mqtt_topic'))
        )
        conn.commit()
        hanger = {
            'id': hanger_id,
            'tag_id': data.get('tag_id'),
            'mqtt_topic': data.get('mqtt_topic')
        }
        conn.close()
        return hanger, 201

@api.route('/hangers/<string:id>')
class Hanger(Resource):
    @api.expect(hanger_model)
    def put(self, id):
        """Met à jour un cintre"""
        data = api.payload
        conn = get_db()
        cur = conn.execute('SELECT * FROM hangers WHERE id = ?', (id,))
        if cur.fetchone() is None:
            conn.close()
            return {'error': 'Hanger not found'}, 404
        conn.execute(
            'UPDATE hangers SET tag_id = ?, mqtt_topic = ? WHERE id = ?',
            (data.get('tag_id'), data.get('mqtt_topic'), id)
        )
        conn.commit()
        conn.close()
        return {'message': 'Hanger updated successfully'}, 200

    def delete(self, id):
        """Supprime un cintre"""
        conn = get_db()
        conn.execute('DELETE FROM hangers WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return {'message': 'Hanger deleted successfully'}, 200

@api.route('/tag')
class TagReader(Resource):
    @api.expect(tag_input_model)
    def post(self):
        """Reçoit un tag lu par un lecteur externe et l'affiche (logique à venir)"""
        data = api.payload
        tag_id = data.get('tag_id')
        app.logger.error(f"Tag reçu : {tag_id}")
        return {'message': f'Tag reçu : {tag_id}'}, 200

@api.route('/orders')
class OrderList(Resource):
    @api.marshal_list_with(order_model)
    def get(self):
        """Récupère toutes les commandes"""
        conn = get_db()
        cur = conn.execute('SELECT * FROM orders')
        orders = []
        for row in cur.fetchall():
            order = dict(row)
            order['items'] = json.loads(order['items']) if order['items'] else []
            orders.append(order)
        conn.close()
        sorted_orders = sorted(orders, key=lambda x: x.get('timestamp', ''), reverse=True)
        return sorted_orders, 200

    @api.expect(order_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """Crée une nouvelle commande (items est une liste JSON)"""
        data = api.payload
        order_id = str(uuid.uuid4())
        items_list = data.get('items', [])
        timestamp = datetime.now().isoformat() + 'Z'
        status = 'En cours'
        conn = get_db()
        conn.execute(
            'INSERT INTO orders (id, items, timestamp, status) VALUES (?, ?, ?, ?)',
            (order_id, json.dumps(items_list), timestamp, status)
        )
        conn.commit()
        order = {
            'id': order_id,
            'items': items_list,
            'timestamp': timestamp,
            'status': status
        }
        conn.close()
        return order, 201

def init_db():
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'a').close()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(item_model_db_init)
    conn.execute(order_model_db_init)
    conn.execute(hanger_model_db_init)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
