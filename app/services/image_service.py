from sqlalchemy.orm import Session
from fastapi import UploadFile
import logging
from typing import List
from app.core.exceptions.image_exceptions import ImageUploadValidationError
from app.core.exceptions.s3_exceptions import S3FileUploadError
from app.repositories.image_repository import ImageRepository
from app.common.constant import Constant
from app.common.message import ErrorMessage
from app.infra.storage.s3 import S3
from app.models.image import Image
from app.schemas.image import ImageUploadResponse
from botocore.exceptions import (
    ClientError,
    BotoCoreError,
)

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.image_repo = ImageRepository(db)
        self.s3 = S3()

    def validate(self, image_file: UploadFile, alt_text: str | None):
        VALUE = "image_file"
        errors = []

        # ファイルサイズチェック
        fileobj = image_file.file
        fileobj.seek(0, 2)
        size = fileobj.tell()
        fileobj.seek(0)
        if size > Constant.MAX_FILE_SIZE:
            errors.append({"value": VALUE, "message": ErrorMessage.MAX_FILE_SIZE})

        # 拡張子チェック
        extension = image_file.filename.split(".")[-1].lower()
        if extension not in Constant.ALLOWED_EXTENSIONS:
            errors.append({"value": VALUE, "message": ErrorMessage.ALLOWED_EXTENSIONS})

        # 代替テキストサイズチェック
        if alt_text and len(alt_text) > Constant.MAX_ALT_TEXT_LENGTH:
            errors.append({"value": VALUE, "message": ErrorMessage.MAX_ALT_TEXT_LENGTH})

        image_file.file.seek(0)

        if errors:
            raise ImageUploadValidationError(errors)

    def upload_file(
        self, image_file: UploadFile, alt_text: str | None
    ) -> ImageUploadResponse:
        image_file.file.seek(0)

        # 一意なファイル名 & 保存パス生成
        unique_key = self.s3.build_unique_key(image_file.filename)

        # s3アップロード処理
        try:
            self.s3.upload_fileobj(image_file.file, unique_key, image_file.content_type)

            url = self.s3.build_public_url(unique_key)

            alt_text = alt_text if alt_text else ""

            image = Image(
                post_id=None,
                url=url,
                alt_text=alt_text,
            )

            new_image_id = self.image_repo.create(image)

            self.db.commit()

            return ImageUploadResponse(
                image_id=new_image_id, url=url, alt_text=alt_text
            )

        except ClientError as e:
            logger.error(
                "S3 ClientError",
                extra={
                    "error": e.response,
                    "key": unique_key,
                },
            )
            self.db.rollback()
            raise S3FileUploadError()

        except BotoCoreError as e:
            logger.exception("S3 BotoCoreError")
            self.db.rollback()
            raise S3FileUploadError()

        except Exception:
            self.db.rollback()
            logger.exception("Unexpected error during image upload")
            raise