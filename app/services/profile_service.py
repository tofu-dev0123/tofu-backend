import logging
from sqlalchemy.orm import Session
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfilePutRequest
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage

logger = logging.getLogger(__name__)


class ProfileService:

    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)

    """
    プロフィールを取得する
    """

    def get_profile(self) -> ProfileResponse:
        profile = self.profile_repo.get()

        if profile is None:
            raise ApplicationError(
                message=ErrorMessage.PROFILE_NOT_EXIST, code=ErrorCode.NOT_EXIST
            )

        return ProfileResponse(
            headline=profile.headline,
            bio=profile.bio,
            site_description=profile.site_description,
        )

    """
    プロフィールを更新する
    """

    def update_profile(self, request: ProfilePutRequest) -> None:
        try:
            profile = self.profile_repo.get()

            if profile is None:
                raise ApplicationError(
                    message=ErrorMessage.PROFILE_NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            self.profile_repo.update(
                profile.profile_id,
                request.headline,
                request.bio,
                request.site_description,
            )

            self.db.commit()

            logger.info("profile updated", extra={"profile_id": profile.profile_id})

        except:
            self.db.rollback()
            raise
