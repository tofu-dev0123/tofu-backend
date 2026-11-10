from unittest.mock import patch

from app.common.errorcode import ErrorCode
from app.common.message import Message, ErrorMessage
from app.core.exceptions.image_exceptions import (
    ImageNotExistError,
    ImageNotExistOnStorageError,
)


@patch("app.services.image_service.ImageService.delete_image")
def test_image_delete_success(
    mock_delete_image,
    client,
    auth_headers,
):
    mock_delete_image.return_value = None

    response = client.delete(
        "admin/images/1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["message"] == Message.IMAGE_DELETE_SUCCESS
    mock_delete_image.assert_called_once_with(1)


@patch(
    "app.services.image_service.ImageService.delete_image",
    side_effect=ImageNotExistError(),
)
def test_image_delete_not_found(
    mock_delete_image,
    client,
    auth_headers,
):
    response = client.delete(
        "admin/images/999",
        headers=auth_headers,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST
    mock_delete_image.assert_called_once_with(999)


@patch(
    "app.services.image_service.ImageService.delete_image",
    side_effect=ImageNotExistOnStorageError(),
)
def test_image_delete_not_exist_on_storage(
    mock_delete_image,
    client,
    auth_headers,
):
    response = client.delete(
        "admin/images/1",
        headers=auth_headers,
    )

    assert response.status_code == 400

    data = response.json()
    assert data["error"] == ErrorCode.NOT_EXIST_ON_STORAGE
    assert data["message"] == ErrorMessage.NOT_EXIST_ON_STORAGE
