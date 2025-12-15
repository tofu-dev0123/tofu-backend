from app.infra.storage.s3_client import get_s3_client
from app.core.config import settings

def upload_fileobj(fileobj, key: str, content_type: str):
    s3 = get_s3_client()

    s3.upload_fileobj(
        fileobj,
        settings.S3_BUCKET_NAME,
        key,
        ExtraArgs={
            "ContentType": content_type,
            "CacheControl": "max-age=31536000",
        },
    )

def delete_object(key: str):
    s3 = get_s3_client()
    s3.delete_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
    )
