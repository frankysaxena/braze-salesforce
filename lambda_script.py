import json
import boto3
import urllib3
import gzip
from urllib.parse import urlencode
from botocore.exceptions import ClientError

http = urllib3.PoolManager()
s3 = boto3.client('s3')

def get_secret():
    secret_name = "salesforce-credentials"
    region_name = "us-east-1"  # Replace with your AWS region if different

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def process_s3_file(bucket, key):
    try:
        print(f"Attempting to retrieve object from bucket: {bucket}, key: {key}")
        response = s3.get_object(Bucket=bucket, Key=key)
        print(f"S3 get_object response metadata: {response['ResponseMetadata']}")
        
        content = response['Body'].read()
        print(f"Raw content length: {len(content)} bytes")
        
        try:
            # Try to decompress as gzip
            print("Attempting gzip decompression.")
            decompressed = gzip.decompress(content)
            print("Gzip decompression successful.")
            json_content = json.loads(decompressed)
        except (OSError, gzip.BadGzipFile) as e:
            print(f"Gzip decompression failed: {e}, attempting to parse content as JSON directly.")
            # If gzip decompression fails, try to parse as JSON directly
            json_content = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed after gzip decompression: {e}")
            raise
        
        print(f"Processed file content: {json_content}")
        return json_content
    except Exception as e:
        print(f"Error in process_s3_file: {e}")
        raise


def lambda_handler(event, context):
    # Process S3 event
    print("Lambda function started")
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        print(f"Processing file {key} from bucket {bucket}")
        
        print("About to process S3 file")
        file_content = process_s3_file(bucket, key)
        print("S3 file processed successfully")
        print(f"File content: {json.dumps(file_content)}")
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing S3 file: {str(e)}')
        }

    # Check if required fields are present in the file content
    if 'campaign_name' not in file_content or 'html_body' not in file_content:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required fields in the file: campaign_name or html_body')
        }

    # Retrieve Salesforce credentials from AWS Secrets Manager
    try:
        sf_creds = get_secret()
        print(f"Retrieved secret keys: {', '.join(sf_creds.keys())}")
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error retrieving secrets: {str(e)}')
        }

    # Check if all required keys are present
    required_keys = ['SF_CLIENT_ID', 'SF_CLIENT_SECRET', 'SF_USERNAME', 'SF_PASSWORD', 'SF_SECURITY_TOKEN']
    missing_keys = [key for key in required_keys if key not in sf_creds]
    if missing_keys:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Missing required keys in secret: {", ".join(missing_keys)}')
        }

    # Salesforce authentication
    auth_url = "<<salesforce_auth_url>>"
    auth_data = {
        "grant_type": "password",
        "client_id": sf_creds['SF_CLIENT_ID'],
        "client_secret": sf_creds['SF_CLIENT_SECRET'],
        "username": sf_creds['SF_USERNAME'],
        "password": sf_creds['SF_PASSWORD'] + sf_creds['SF_SECURITY_TOKEN']
    }
    
    encoded_auth_data = urlencode(auth_data)
    auth_response = http.request('POST', auth_url, 
                                 body=encoded_auth_data,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    if auth_response.status != 200:
        return {
            'statusCode': auth_response.status,
            'body': json.dumps(f'Authentication failed: {auth_response.data.decode("utf-8")}')
        }
    
    auth_json = json.loads(auth_response.data.decode('utf-8'))
    access_token = auth_json['access_token']
    instance_url = auth_json['instance_url']
    
    BrazeEmailsObject = "BrazeEmails__c" # Custom object in Salesforce that you create and ensure that this is correctly setup in Salesforce

    # BrazeEmails creation operation
    braze_email_url = f"{instance_url}/services/data/v58.0/sobjects/{BrazeEmailsObject}/"
    braze_email_data = {
        "Name": file_content['campaign_name'],
        "HTML__c": file_content['html_body'],
        "Contact__c": file_content['external_id']
    }
    
    braze_email_response = http.request('POST', braze_email_url,
                                        body=json.dumps(braze_email_data),
                                        headers={
                                            'Authorization': f'Bearer {access_token}',
                                            'Content-Type': 'application/json'
                                        })
    
    if braze_email_response.status != 201:
        return {
            'statusCode': braze_email_response.status,
            'body': json.dumps(f'Error creating BrazeEmail: {braze_email_response.data.decode("utf-8")}')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('BrazeEmail created successfully')
    }