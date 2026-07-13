from sqlalchemy.orm import Session
from app.repositories.profile_repository import ProfileRepository
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.profile import ProfileResponse, AboutResponse
from app.schemas.timeline import Timeline


class PublicAboutService:

    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.timeline_repo = TimelineRepository(db)

    """
    About ページ表示用のプロフィールと年表を取得する
    """

    def get_about(self) -> AboutResponse:
        profile = self.profile_repo.get()

        if profile is None:
            profile_data = ProfileResponse(headline="", bio="", site_description="")
        else:
            profile_data = ProfileResponse(
                headline=profile.headline,
                bio=profile.bio,
                site_description=profile.site_description,
            )

        timelines = self.timeline_repo.find_all()
        timeline_list = [
            Timeline(
                timeline_id=t.timeline_id,
                year=t.year,
                title=t.title,
                body=t.body,
                sort_order=t.sort_order,
            )
            for t in timelines
        ]

        return AboutResponse(profile=profile_data, timelines=timeline_list)
