import boto3
import uuid
from urllib.parse import urlparse
from datetime import datetime
from app.core.config import settings
from botocore.exceptions import ClientError


class S3:

    def __init__(self):
        self.env = settings.APP_ENV
        self.ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        self.SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        self.REGION_NAME = settings.AWS_DEFAULT_REGION
        self.ENDPOINT_URL = settings.S3_ENDPOINT_URL
        self.BUCKET_NAME = settings.S3_BUCKET_NAME
        self.CLOUDFRONT_DOMAIN = settings.CLOUDFRONT_DOMAIN

    def get_s3_client(self):
        kwargs = {
            "service_name": "s3",
            "aws_access_key_id": self.ACCESS_KEY_ID,
            "aws_secret_access_key": self.SECRET_ACCESS_KEY,
            "region_name": self.REGION_NAME,
        }

        # LocalStack は local 環境のみ
        if self.env == "local" and self.ENDPOINT_URL:
            kwargs["endpoint_url"] = self.ENDPOINT_URL

        return boto3.client(**kwargs)

    def upload_fileobj(self, fileobj, key: str, content_type: str):
        s3 = self.get_s3_client()

        try:
            s3.upload_fileobj(
                fileobj,
                self.BUCKET_NAME,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "CacheControl": "max-age=31536000",
                },
            )
        except ClientError as e:
            print("S3 upload failed:", e)
            raise

    def delete_object(self, key: str):
        s3 = self.get_s3_client()
        s3.delete_object(
            Bucket=self.BUCKET_NAME,
            Key=key,
        )

    def build_unique_key(self, filename: str) -> str:
        today = datetime.now()
        ext = filename.split(".")[-1].lower()
        file_name = f"{uuid.uuid4()}.{ext}"
        object_key = f"images/{today:%Y}/{today:%m}/{today:%d}/{file_name}"

        return f"{object_key}"

    def build_public_url(self, key: str) -> str:
        if self.env == "local":
            return f"http://localhost:4566/{self.BUCKET_NAME}/{key}"

        if self.CLOUDFRONT_DOMAIN:
            return f"https://{self.CLOUDFRONT_DOMAIN}/{key}"

        return f"https://{self.BUCKET_NAME}.s3.amazonaws.com/{key}"

    def extract_key_from_url(self, url: str) -> str:
        """
        public URL から S3 の object key を抽出する
        """
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")

        # local (localhost:4566/bucket/key)
        if self.env == "local":
            if not path.startswith(f"{self.BUCKET_NAME}/"):
                raise ValueError("Invalid S3 local URL")
            return path.replace(f"{self.BUCKET_NAME}/", "", 1)

        # cloudfront or s3
        return path

    def exists(self, key: str) -> bool:
        s3 = self.get_s3_client()
        try:
            s3.head_object(
                Bucket=self.BUCKET_NAME,
                Key=key,
            )
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("404", "NoSuchKey", "NotFound"):
                return False
            raise

    def exists_by_url(self, url: str) -> bool:
        key = self.extract_key_from_url(url)
        return self.exists(key)
