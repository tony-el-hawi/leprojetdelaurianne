#!/usr/bin/env python3
import boto3
import uuid
import requests
import random
import os

# Configuration
PROJECT_NAME = "le-projet-de-laurianne"
REGION = "eu-west-1"
PROFILE = "soper"

# Mock data
CATEGORIES = ["Jupes", "Shorts", "Jeans", "Blouses", "Chemises"]

MOCK_ITEMS = [
    {"name": "Jean vert délavé", "category": "Jeans", "color": "Vert", "size": "38", "image_url": "jean1.jpg"},
    {"name": "Jean bleu classique", "category": "Jeans", "color": "Bleu", "size": "40", "image_url": "jean2.jpg"},
    {"name": "Jean noir slim", "category": "Jeans", "color": "Noir", "size": "36", "image_url": "jean3.jpg"},
    {"name": "Jean brut indigo", "category": "Jeans", "color": "Indigo", "size": "42", "image_url": "jean4.jpg"},
    {"name": "Jupe plissée marine", "category": "Jupes", "color": "Marine", "size": "S", "image_url": "jupe1.jpg"},
    {"name": "Jupe évasée rouge", "category": "Jupes", "color": "Rouge", "size": "M", "image_url": "jupe2.jpg"},
    {"name": "Jupe crayon beige", "category": "Jupes", "color": "Beige", "size": "L", "image_url": "jupe3.jpg"},
    {"name": "Jupe longue fleurie", "category": "Jupes", "color": "Multicolore", "size": "M", "image_url": "jupe4.jpg"},
    {"name": "Short denim clair", "category": "Shorts", "color": "Bleu clair", "size": "34", "image_url": "short1.jpg"},
    {"name": "Short cargo kaki", "category": "Shorts", "color": "Kaki", "size": "36", "image_url": "short2.jpg"},
    {"name": "Short blanc estival", "category": "Shorts", "color": "Blanc", "size": "38", "image_url": "short3.jpg"},
    {"name": "Short noir élégant", "category": "Shorts", "color": "Noir", "size": "40", "image_url": "short4.jpg"}
]

def get_bucket_name():
    """Get the S3 bucket name from Terraform state"""
    try:
        session = boto3.Session(profile_name=PROFILE)
        s3 = session.client('s3', region_name=REGION)
        buckets = s3.list_buckets()['Buckets']
        for bucket in buckets:
            if PROJECT_NAME in bucket['Name'] and 'images' in bucket['Name']:
                return bucket['Name']
    except Exception as e:
        print(f"Error finding bucket: {e}")
    return None

def upload_image_to_s3(image_path, bucket_name, key):
    """Read local image and upload to S3"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        session = boto3.Session(profile_name=PROFILE)
        s3 = session.client('s3', region_name=REGION)
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=image_data,
            ContentType='image/jpeg'
        )
        return f"https://{bucket_name}.s3.amazonaws.com/{key}"
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def inject_mock_data():
    """Inject mock data into DynamoDB and S3"""
    session = boto3.Session(profile_name=PROFILE)
    dynamodb = session.resource('dynamodb', region_name=REGION)
    table_name = f"{PROJECT_NAME}-items"
    table = dynamodb.Table(table_name)
    
    bucket_name = get_bucket_name()
    if not bucket_name:
        print("Could not find S3 bucket. Make sure Terraform has been applied.")
        return
    
    print(f"Using table: {table_name}")
    print(f"Using bucket: {bucket_name}")
    
    for item_data in MOCK_ITEMS:
        item_id = str(uuid.uuid4())
        photo_key = f"items/{item_id}.jpg"
        
        # Upload image to S3
        img_path = os.path.join(os.path.dirname(__file__), 'img', item_data['image_url'])
        photo_url = upload_image_to_s3(img_path, bucket_name, photo_key)
        
        # Create DynamoDB item
        item = {
            'id': item_id,
            'name': item_data['name'],
            'category': item_data['category'],
            'color': item_data['color'],
            'size': item_data['size'],
            'photo': photo_url,
            'mock': True
        }
        
        table.put_item(Item=item)
        print(f"✓ Added: {item_data['name']}")
    
    print(f"\n🎉 Successfully injected {len(MOCK_ITEMS)} items!")

if __name__ == "__main__":
    inject_mock_data()