from unittest.mock import patch
from app.schemas.image import ImageUploadResponse
from app.core.exceptions.image_exceptions import ImageUploadValidationError
from app.common.errorcode import ErrorCode
from app.core.exceptions.s3_exceptions import S3FileUploadError


@patch("app.services.image_service.ImageService.upload_file")
@patch("app.services.image_service.ImageService.validate")
def test_image_upload_success(
    mock_validate,
    mock_upload_file,
    client,
    valid_token,
):
    mock_validate.return_value = None
    mock_upload_file.return_value = ImageUploadResponse(
        image_id=1,
        url="https://cdn.example.com/test.png",
        alt_text="alt",
    )

    files = {
        "image_file": ("test.png", b"dummy image", "image/png"),
    }
    data = {
        "alt_text": "alt",
    }

    response = client.post(
        "admin/images/upload",
        headers={"Authorization": f"Bearer {valid_token}"},
        files=files,
        data=data,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["image_id"] == 1
    assert body["url"] == "https://cdn.example.com/test.png"
    assert body["alt_text"] == "alt"

    mock_validate.assert_called_once()
    mock_upload_file.assert_called_once()


@patch(
    "app.services.image_service.ImageService.validate",
    side_effect=ImageUploadValidationError(
        [{"value": "image_file", "message": "error"}]
    ),
)
def test_image_upload_validation_error(
    mock_validate,
    client,
    valid_token,
):
    files = {
        "image_file": ("test.png", b"dummy image", "image/png"),
    }

    response = client.post(
        "admin/images/upload",
        headers={"Authorization": f"Bearer {valid_token}"},
        files=files,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.VALIDATION_ERROR


@patch(
    "app.services.image_service.ImageService.upload_file",
    side_effect=S3FileUploadError(),
)
@patch("app.services.image_service.ImageService.validate")
def test_image_upload_s3_error(
    mock_validate,
    mock_upload_file,
    client,
    valid_token,
):
    files = {
        "image_file": ("test.png", b"dummy image", "image/png"),
    }

    response = client.post(
        "admin/images/upload",
        headers={"Authorization": f"Bearer {valid_token}"},
        files=files,
    )

    assert response.status_code == 400
