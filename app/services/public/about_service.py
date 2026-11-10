from sqlalchemy.orm import Session
from app.repositories.profile_repository import ProfileRepository
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.profile import ProfileResponse, AboutResponse
from app.services.mappers import to_profile, to_timeline


class PublicAboutService:

    def __init__(
        self,
        db: Session,
        profile_repo: ProfileRepository | None = None,
        timeline_repo: TimelineRepository | None = None,
    ) -> None:
        self.db = db
        self.profile_repo = profile_repo or ProfileRepository(db)
        self.timeline_repo = timeline_repo or TimelineRepository(db)

    """
    About ページ表示用のプロフィールと年表を取得する
    """

    def get_about(self) -> AboutResponse:
        profile = self.profile_repo.get()

        if profile is None:
            profile_data = ProfileResponse(headline="", bio="", site_description="")
        else:
            profile_data = to_profile(profile)

        timelines = self.timeline_repo.find_all()
        timeline_list = [to_timeline(t) for t in timelines]

        return AboutResponse(profile=profile_data, timelines=timeline_list)
