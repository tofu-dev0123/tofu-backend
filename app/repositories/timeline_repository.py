from datetime import datetime
from sqlalchemy import select, update, delete, exists
from sqlalchemy.orm import Session
from app.models.timeline import Timeline


class TimelineRepository:

    def __init__(self, db: Session):
        self.db = db

    def exist_check(self, timeline_id: int) -> bool:
        stmt = select(exists().where(Timeline.timeline_id == timeline_id))
        return bool(self.db.execute(stmt).scalar())

    def find_all(self):
        stmt = select(Timeline).order_by(
            Timeline.sort_order.asc(), Timeline.year.desc()
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_id(self, timeline_id: int) -> Timeline | None:
        return (
            self.db.query(Timeline)
            .filter(Timeline.timeline_id == timeline_id)
            .first()
        )

    def create(self, timeline: Timeline) -> int:
        self.db.add(timeline)
        self.db.flush()
        return timeline.timeline_id

    def update(
        self,
        timeline_id: int,
        year: int,
        title: str | None,
        body: str | None,
        sort_order: int,
    ) -> None:
        stmt = (
            update(Timeline)
            .where(Timeline.timeline_id == timeline_id)
            .values(
                year=year,
                title=title,
                body=body,
                sort_order=sort_order,
                updated_at=datetime.now(),
            )
        )
        self.db.execute(stmt)

    def delete(self, timeline_id: int) -> None:
        stmt = delete(Timeline).where(Timeline.timeline_id == timeline_id)
        self.db.execute(stmt)
