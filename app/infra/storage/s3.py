import boto3
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import BinaryIO
from urllib.parse import urlparse
from datetime import datetime
from app.core.config import Settings, settings
from botocore.client import BaseClient
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# delete_objects で 1 リクエストに指定できるキー数の上限
S3_DELETE_OBJECTS_MAX_KEYS = 1000


@dataclass(frozen=True)
class S3Config:
    """S3 接続・URL 組み立てに使う設定値"""

    env: str
    access_key_id: str | None
    secret_access_key: str | None
    region_name: str | None
    endpoint_url: str | None
    bucket_name: str | None
    cloudfront_domain: str | None

    @classmethod
    def from_settings(cls, settings: Settings) -> "S3Config":
        return cls(
            env=settings.APP_ENV,
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            # S3 バケットのリージョン。本番は Lambda の AWS_REGION (us-east-1) に
            # フォールバックさせず、バケットの実リージョンを明示する必要がある。
            region_name=settings.S3_REGION or settings.AWS_DEFAULT_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            bucket_name=settings.S3_BUCKET_NAME,
            cloudfront_domain=settings.CLOUDFRONT_DOMAIN,
        )


def _generate_id() -> str:
    return str(uuid.uuid4())


class S3:

    def __init__(
        self,
        config: S3Config | None = None,
        client: BaseClient | None = None,
        now: Callable[[], datetime] = datetime.now,
        id_factory: Callable[[], str] = _generate_id,
    ) -> None:
        self.config = config or S3Config.from_settings(settings)
        self._client = client
        self.now = now
        self.id_factory = id_factory

    def get_s3_client(self) -> BaseClient:
        if self._client is not None:
            return self._client

        kwargs = {
            "service_name": "s3",
            "region_name": self.config.region_name,
        }

        # local (LocalStack) のみ明示クレデンシャルとエンドポイントを使う。
        # 本番 (Lambda) は実行ロールの一時クレデンシャルを使うため明示キーを渡さない。
        # Lambda ランタイムが自動設定する一時アクセスキーを session token 無しで
        # 渡すと InvalidAccessKeyId になるため、boto3 の既定の認証チェーンに任せる。
        if self.config.env == "local":
            kwargs["aws_access_key_id"] = self.config.access_key_id
            kwargs["aws_secret_access_key"] = self.config.secret_access_key
            if self.config.endpoint_url:
                kwargs["endpoint_url"] = self.config.endpoint_url

        return boto3.client(**kwargs)

    def upload_fileobj(self, fileobj: BinaryIO, key: str, content_type: str) -> None:
        s3 = self.get_s3_client()

        try:
            s3.upload_fileobj(
                fileobj,
                self.config.bucket_name,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "CacheControl": "max-age=31536000",
                },
            )
        except ClientError:
            logger.exception("S3 upload failed", extra={"key": key})
            raise

    def delete_object(self, key: str) -> None:
        s3 = self.get_s3_client()
        s3.delete_object(
            Bucket=self.config.bucket_name,
            Key=key,
        )

    def delete_objects(self, keys: list[str]) -> list[str]:
        """
        複数オブジェクトをまとめて削除し、削除に失敗したキーを返す。
        delete_objects はキー単位の失敗を例外ではなくレスポンスの Errors で返す。
        """
        if not keys:
            return []

        s3 = self.get_s3_client()
        failed_keys: list[str] = []

        # 1 リクエストあたりのキー数上限ごとに分割する
        for i in range(0, len(keys), S3_DELETE_OBJECTS_MAX_KEYS):
            chunk = keys[i : i + S3_DELETE_OBJECTS_MAX_KEYS]
            response = s3.delete_objects(
                Bucket=self.config.bucket_name,
                Delete={"Objects": [{"Key": key} for key in chunk], "Quiet": True},
            )
            failed_keys.extend(error["Key"] for error in response.get("Errors", []))

        return failed_keys

    def build_unique_key(self, filename: str) -> str:
        today = self.now()
        ext = filename.split(".")[-1].lower()
        file_name = f"{self.id_factory()}.{ext}"
        object_key = f"images/{today:%Y}/{today:%m}/{today:%d}/{file_name}"

        return f"{object_key}"

    def build_public_url(self, key: str) -> str:
        if self.config.env == "local":
            return f"http://localhost:4566/{self.config.bucket_name}/{key}"

        if self.config.cloudfront_domain:
            return f"https://{self.config.cloudfront_domain}/{key}"

        return f"https://{self.config.bucket_name}.s3.amazonaws.com/{key}"

    def extract_key_from_url(self, url: str) -> str:
        """
        public URL から S3 の object key を抽出する
        """
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")

        # local (localhost:4566/bucket/key)
        if self.config.env == "local":
            if not path.startswith(f"{self.config.bucket_name}/"):
                raise ValueError("Invalid S3 local URL")
            return path.replace(f"{self.config.bucket_name}/", "", 1)

        # cloudfront or s3
        return path

    def exists(self, key: str) -> bool:
        s3 = self.get_s3_client()
        try:
            s3.head_object(
                Bucket=self.config.bucket_name,
                Key=key,
            )
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("404", "NoSuchKey", "NotFound"):
                return False
            raise
