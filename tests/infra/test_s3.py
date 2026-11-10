import pytest
from io import BytesIO
from datetime import datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from app.infra.storage.s3 import S3, S3Config


def _config(**overrides: Any) -> S3Config:
    values: dict[str, Any] = dict(
        env="production",
        access_key_id="key",
        secret_access_key="secret",
        region_name="ap-northeast-1",
        endpoint_url=None,
        bucket_name="bucket",
        cloudfront_domain="cdn.example.com",
    )
    values.update(overrides)
    return S3Config(**values)


def _client_error(code: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": ""}}, "HeadObject")


# ==================== S3Config ====================


# settings から設定値を組み立てる（S3_REGION を優先）
def test_config_from_settings():
    settings = SimpleNamespace(
        APP_ENV="local",
        AWS_ACCESS_KEY_ID="key",
        AWS_SECRET_ACCESS_KEY="secret",
        AWS_DEFAULT_REGION="us-east-1",
        S3_REGION="ap-northeast-1",
        S3_ENDPOINT_URL="http://localstack:4566",
        S3_BUCKET_NAME="bucket",
        CLOUDFRONT_DOMAIN=None,
    )

    config = S3Config.from_settings(settings)  # type: ignore[arg-type]

    assert config == S3Config(
        env="local",
        access_key_id="key",
        secret_access_key="secret",
        region_name="ap-northeast-1",
        endpoint_url="http://localstack:4566",
        bucket_name="bucket",
        cloudfront_domain=None,
    )


# S3_REGION が未設定なら AWS_DEFAULT_REGION にフォールバックする
def test_config_from_settings_region_fallback():
    settings = SimpleNamespace(
        APP_ENV="production",
        AWS_ACCESS_KEY_ID=None,
        AWS_SECRET_ACCESS_KEY=None,
        AWS_DEFAULT_REGION="us-east-1",
        S3_REGION=None,
        S3_ENDPOINT_URL=None,
        S3_BUCKET_NAME="bucket",
        CLOUDFRONT_DOMAIN="cdn.example.com",
    )

    config = S3Config.from_settings(settings)  # type: ignore[arg-type]

    assert config.region_name == "us-east-1"


# ==================== get_s3_client ====================


# 注入したクライアントをそのまま使う
def test_get_s3_client_injected():
    client = MagicMock()
    s3 = S3(config=_config(), client=client)

    assert s3.get_s3_client() is client


# local は明示クレデンシャルとエンドポイントを渡す
@patch("app.infra.storage.s3.boto3.client")
def test_get_s3_client_local(mock_boto_client):
    s3 = S3(config=_config(env="local", endpoint_url="http://localstack:4566"))

    s3.get_s3_client()

    mock_boto_client.assert_called_once_with(
        service_name="s3",
        region_name="ap-northeast-1",
        aws_access_key_id="key",
        aws_secret_access_key="secret",
        endpoint_url="http://localstack:4566",
    )


# local 以外は既定の認証チェーンに任せる（クレデンシャルを渡さない）
@patch("app.infra.storage.s3.boto3.client")
def test_get_s3_client_production(mock_boto_client):
    s3 = S3(config=_config())

    s3.get_s3_client()

    mock_boto_client.assert_called_once_with(
        service_name="s3", region_name="ap-northeast-1"
    )


# ==================== upload / delete / exists ====================


def test_upload_fileobj():
    client = MagicMock()
    s3 = S3(config=_config(), client=client)
    fileobj = BytesIO(b"data")

    s3.upload_fileobj(fileobj, "images/a.png", "image/png")

    client.upload_fileobj.assert_called_once_with(
        fileobj,
        "bucket",
        "images/a.png",
        ExtraArgs={"ContentType": "image/png", "CacheControl": "max-age=31536000"},
    )


# アップロード失敗時は ERROR ログを出して再送出する
def test_upload_fileobj_client_error(caplog):
    client = MagicMock()
    client.upload_fileobj.side_effect = _client_error("500")
    s3 = S3(config=_config(), client=client)

    with pytest.raises(ClientError):
        s3.upload_fileobj(BytesIO(b"data"), "images/a.png", "image/png")

    assert any(
        r.levelname == "ERROR" and r.getMessage() == "S3 upload failed"
        for r in caplog.records
    )


def test_delete_object():
    client = MagicMock()
    s3 = S3(config=_config(), client=client)

    s3.delete_object("images/a.png")

    client.delete_object.assert_called_once_with(Bucket="bucket", Key="images/a.png")


def test_exists_true():
    client = MagicMock()
    s3 = S3(config=_config(), client=client)

    assert s3.exists("images/a.png") is True
    client.head_object.assert_called_once_with(Bucket="bucket", Key="images/a.png")


@pytest.mark.parametrize("code", ["404", "NoSuchKey", "NotFound"])
def test_exists_not_found(code):
    client = MagicMock()
    client.head_object.side_effect = _client_error(code)
    s3 = S3(config=_config(), client=client)

    assert s3.exists("images/a.png") is False


# 存在しない以外のエラーは再送出する
def test_exists_other_error():
    client = MagicMock()
    client.head_object.side_effect = _client_error("403")
    s3 = S3(config=_config(), client=client)

    with pytest.raises(ClientError):
        s3.exists("images/a.png")


# ==================== key / URL ====================


# 注入した時刻と ID でキーを組み立てる（拡張子は小文字化）
def test_build_unique_key():
    s3 = S3(
        config=_config(),
        now=lambda: datetime(2025, 1, 2, 3, 4, 5),
        id_factory=lambda: "fixed-id",
    )

    assert s3.build_unique_key("photo.PNG") == "images/2025/01/02/fixed-id.png"


def test_build_public_url_local():
    s3 = S3(config=_config(env="local"))

    assert s3.build_public_url("images/a.png") == "http://localhost:4566/bucket/images/a.png"


def test_build_public_url_cloudfront():
    s3 = S3(config=_config())

    assert s3.build_public_url("images/a.png") == "https://cdn.example.com/images/a.png"


def test_build_public_url_s3():
    s3 = S3(config=_config(cloudfront_domain=None))

    assert (
        s3.build_public_url("images/a.png")
        == "https://bucket.s3.amazonaws.com/images/a.png"
    )


def test_extract_key_from_url_local():
    s3 = S3(config=_config(env="local"))

    assert (
        s3.extract_key_from_url("http://localhost:4566/bucket/images/a.png")
        == "images/a.png"
    )


# local でバケット名から始まらない URL は不正
def test_extract_key_from_url_local_invalid():
    s3 = S3(config=_config(env="local"))

    with pytest.raises(ValueError):
        s3.extract_key_from_url("http://localhost:4566/other/images/a.png")


def test_extract_key_from_url_cloudfront():
    s3 = S3(config=_config())

    assert (
        s3.extract_key_from_url("https://cdn.example.com/images/a.png")
        == "images/a.png"
    )
