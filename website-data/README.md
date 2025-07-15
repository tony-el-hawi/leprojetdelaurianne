# Mock Data Injection

This script injects mock clothing items into your DynamoDB table and uploads sample images to S3.

## Usage

1. Make sure your AWS credentials are configured
2. Deploy your infrastructure with Terraform first
3. Install dependencies: `pip install -r requirements.txt`
4. Run the script: `python inject_mock_data.py`

The script will automatically:
- Find your DynamoDB table and S3 bucket
- Download sample images from Picsum
- Upload them to your S3 bucket
- Create 20 clothing items in DynamoDB with proper image URLs