from app.core.config import settings

def build_public_url(key: str) -> str:
    if settings.APP_ENV == "local":
        return f"http://localhost:4566/{settings.S3_BUCKET_NAME}/{key}"

    if settings.CLOUDFRONT_DOMAIN:
        return f"https://{settings.CLOUDFRONT_DOMAIN}/{key}"

    return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{key}"
        