import logging
from sqlalchemy.orm import Session
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfilePutRequest
from app.common.message import ErrorMessage
from app.services.transaction import transaction
from app.services.guards import ensure_exists

logger = logging.getLogger(__name__)


class ProfileService:

    def __init__(
        self,
        db: Session,
        profile_repo: ProfileRepository | None = None,
    ) -> None:
        self.db = db
        self.profile_repo = profile_repo or ProfileRepository(db)

    """
    プロフィールを取得する
    """

    def get_profile(self) -> ProfileResponse:
        profile = ensure_exists(self.profile_repo.get(), ErrorMessage.PROFILE_NOT_EXIST)

        return ProfileResponse(
            headline=profile.headline,
            bio=profile.bio,
            site_description=profile.site_description,
        )

    """
    プロフィールを更新する
    """

    def update_profile(self, request: ProfilePutRequest) -> None:
        with transaction(self.db):
            profile = ensure_exists(
                self.profile_repo.get(),
                ErrorMessage.PROFILE_NOT_EXIST,
            )

            self.profile_repo.update(
                profile.profile_id,
                request.headline,
                request.bio,
                request.site_description,
            )

        logger.info("profile updated", extra={"profile_id": profile.profile_id})
