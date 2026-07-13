from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.profile import Profile


class ProfileRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self) -> Profile | None:
        stmt = select(Profile).order_by(Profile.profile_id).limit(1)
        return self.db.execute(stmt).scalars().first()

    def update(
        self,
        profile_id: int,
        headline: str,
        bio: str,
        site_description: str,
    ) -> None:
        stmt = (
            update(Profile)
            .where(Profile.profile_id == profile_id)
            .values(
                headline=headline,
                bio=bio,
                site_description=site_description,
                updated_at=datetime.now(),
            )
        )
        self.db.execute(stmt)
