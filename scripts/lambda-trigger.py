import json
import os
import boto3
import requests
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Ensure the file is in the "uploads" directory
    if not key.startswith("uploads/"):
        print("File not in 'uploads' directory. Ignoring.")
        return

    # Get the file extension
    file_extension = os.path.splitext(key)[1]

    try:
        # Download the file from S3 to Lambda temp directory
        local_file_name = '/tmp/' + os.path.basename(key)
        s3.download_file(bucket, key, local_file_name)
    except NoCredentialsError:
        print("No AWS credentials found.")
        return

    # Prepare the data for the Flask API
    data = {
        'file_type': file_extension,
        'source_url': 'demo-chat-verlab-bucket.s3.ap-south-1.amazonaws.com/' + key
    }
    files = {
        'file': open(local_file_name, 'rb')
    }

    # # Call the Flask API
    url = "https://api.kaleido.coursepanel.in/custom-index"  # Replace with your Flask API endpoint
    response = requests.post(url, data=data, files=files)
    
    return 'File successfully processed and indexed', 200

    if response.status_code == 200:
        print(f'Successfully processed file: {key} from bucket: {bucket}')
        
    else:
        print(f'Error processing file: {key} from bucket: {bucket}')
        print(f'Status code: {response.status_code}, Response: {response.text}')
