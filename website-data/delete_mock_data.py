import boto3
import json

def delete_all_mock_data():
    # Initialize AWS clients with profile
    session = boto3.Session(profile_name='soper')
    dynamodb = session.resource('dynamodb')
    s3 = session.client('s3')

    project_name = 'le-projet-de-laurianne-'

    # Find S3 bucket
    bucket_name = None
    for bucket in s3.list_buckets()['Buckets']:
        if project_name in bucket['Name'].lower():
            bucket_name = bucket['Name']
            break
    
    if not bucket_name:
        print("No clothing bucket found")
        return
    
    print(f"Found bucket: {bucket_name}")
    
    # Delete all objects from S3
    objects = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in objects:
        for obj in objects['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            print(f"Deleted S3 object: {obj['Key']}")

    # Find DynamoDB table
    table_name = None
    for table in dynamodb.tables.all():
        if project_name in table.name.lower():
            table_name = table.name
            break
    
    if not table_name:
        print("No clothing table found")
        return
    
    table = dynamodb.Table(table_name)
    print(f"Found table: {table_name}")
    
    # Delete all items from DynamoDB
    response = table.scan()
    items = response['Items']
    
    for item in items:
        table.delete_item(Key={'id': item['id']})
        print(f"Deleted item: {item['name']}")
    
    print("All mock data deleted successfully!")

if __name__ == "__main__":
    delete_all_mock_data()