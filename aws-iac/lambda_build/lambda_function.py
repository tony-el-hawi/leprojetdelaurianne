# GET Items Lambda
import json
import boto3
import os
import uuid
import base64
from datetime import datetime

def handler(event, context):
    method = event["httpMethod"]
    path = event["path"]
    
    if "/orders" in path:
        if method == "GET":
            return get_orders(event, context)
        elif method == "POST":
            return create_order(event, context)
    else:
        if method == "POST":
            return create_item(event, context)
        elif method == "GET":
            return get_items(event, context)
        elif method == "PUT":
            return update_item(event, context)
        elif method == "DELETE":
            return delete_item(event, context)
    
    return {"statusCode": 405, "body": "Method Not Allowed"}

def get_items(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    try:
        response = table.scan()
        items = response['Items']
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps(items)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def create_item(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    bucket = os.environ['BUCKET_NAME']
    
    try:
        body = json.loads(event['body'])
        item_id = str(uuid.uuid4())
        
        # Handle photo upload to S3
        photo_url = None
        if body.get('photo'):
            photo_data = body['photo'].split(',')[1]  # Remove data:image/jpeg;base64,
            photo_key = f"items/{item_id}.jpg"
            
            s3.put_object(
                Bucket=bucket,
                Key=photo_key,
                Body=base64.b64decode(photo_data),
                ContentType='image/jpeg'
            )
            photo_url = f"https://{bucket}.s3.amazonaws.com/{photo_key}"
        
        item = {
            'id': item_id,
            'name': body['name'],
            'category': body['category'],
            'color': body['color'],
            'size': body['size'],
            'photo': photo_url
        }
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 201,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(item)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

# UPDATE Item Lambda
def update_item(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    try:
        item_id = event['pathParameters']['id']
        body = json.loads(event['body'])
        
        table.update_item(
            Key={'id': item_id},
            UpdateExpression='SET #name = :name, category = :category, color = :color, size = :size',
            ExpressionAttributeNames={'#name': 'name'},
            ExpressionAttributeValues={
                ':name': body['name'],
                ':category': body['category'],
                ':color': body['color'],
                ':size': body['size']
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Item updated successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

# DELETE Item Lambda
def delete_item(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    s3 = boto3.client('s3')

    try:
        item_id = event['pathParameters']['id']
        
        table.delete_item(Key={'id': item_id})
        s3.delete_object(Bucket=os.environ['BUCKET_NAME'], Key=f"items/{item_id}.jpg")
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Item deleted successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def get_orders(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['ORDERS_TABLE'])
    
    try:
        response = table.scan()
        orders = response['Items']
        orders.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps(orders)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def create_order(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['ORDERS_TABLE'])
    
    try:
        body = json.loads(event['body'])
        order_id = str(uuid.uuid4())
        
        order = {
            'id': order_id,
            'items': body['items'],
            'timestamp': datetime.now().isoformat() + 'Z',
            'status': 'En cours'
        }
        
        table.put_item(Item=order)
        
        return {
            'statusCode': 201,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(order)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }