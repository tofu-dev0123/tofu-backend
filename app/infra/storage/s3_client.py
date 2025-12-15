import boto3
import os

def get_s3_client():
    endpoint_url = os.getenv("S3_ENDPOINT_URL")

    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        endpoint_url=endpoint_url if endpoint_url else None,
    )