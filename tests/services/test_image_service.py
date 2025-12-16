import pytest
from io import BytesIO
from fastapi import UploadFile
from starlette.datastructures import Headers
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from app.services.image_service import ImageService
from app.core.exceptions.image_exceptions import ImageUploadValidationError
from app.core.exceptions.s3_exceptions import S3FileUploadError
from app.schemas.image import ImageUploadResponse
from app.common.constant import Constant


def test_validate_success(image_service, upload_file):
    image_service.validate(upload_file, alt_text="alt text")


def test_validate_file_size_error(image_service):
    big_file = UploadFile(
        filename="test.png",
        file=BytesIO(b"a" * (Constant.MAX_FILE_SIZE + 1)),
        headers=Headers({"content-type": "image/png"}),
    )

    with pytest.raises(ImageUploadValidationError):
        image_service.validate(big_file, None)


def test_validate_extension_error(image_service):
    file = UploadFile(
        filename="test.exe",
        file=BytesIO(b"dummy"),
        headers=Headers({"content-type": "application/octet-stream"}),
    )

    with pytest.raises(ImageUploadValidationError):
        image_service.validate(file, None)
        

def test_validate_alt_text_length_error(image_service, upload_file):
    alt_text = "a" * (Constant.MAX_ALT_TEXT_LENGTH + 1)

    with pytest.raises(ImageUploadValidationError):
        image_service.validate(upload_file, alt_text)


def test_upload_file_success(image_service, upload_file):
    image_service.image_repo = MagicMock()
    image_service.image_repo.create.return_value = 1

    image_service.s3 = MagicMock()
    image_service.s3.build_unique_key.return_value = "images/2025/01/test.png"
    image_service.s3.build_public_url.return_value = "https://cdn.example.com/test.png"

    result = image_service.upload_file(upload_file, alt_text="alt")

    assert isinstance(result, ImageUploadResponse)
    assert result.image_id == 1
    assert result.url == "https://cdn.example.com/test.png"
    assert result.alt_text == "alt"

    image_service.s3.upload_fileobj.assert_called_once()
    image_service.image_repo.create.assert_called_once()
    image_service.db.commit.assert_called_once()


def test_upload_file_s3_error(image_service, upload_file):
    image_service.s3 = MagicMock()
    image_service.s3.build_unique_key.return_value = "key"
    image_service.s3.upload_fileobj.side_effect = ClientError({}, "PutObject")

    with pytest.raises(S3FileUploadError):
        image_service.upload_file(upload_file, None)

    image_service.db.commit.assert_not_called()


def test_upload_file_db_error(image_service, upload_file):
    image_service.s3 = MagicMock()
    image_service.s3.build_unique_key.return_value = "key"
    image_service.s3.build_public_url.return_value = "url"

    image_service.image_repo = MagicMock()
    image_service.image_repo.create.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        image_service.upload_file(upload_file, None)

    image_service.db.rollback.assert_called_once()
