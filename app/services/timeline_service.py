from sqlalchemy.orm import Session
from app.repositories.timeline_repository import TimelineRepository
from app.models.timeline import Timeline as TimelineModel
from app.schemas.timeline import (
    Timeline,
    TimelineListResponse,
    TimelinePostRequest,
    TimelinePutRequest,
)
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


class TimelineService:

    def __init__(self, db: Session):
        self.db = db
        self.timeline_repo = TimelineRepository(db)

    """
    年表一覧を取得する
    """

    def get_timelines(self) -> TimelineListResponse:
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

        return TimelineListResponse(timelines=timeline_list)

    """
    年表を作成する
    """

    def create_timeline(self, request: TimelinePostRequest) -> int:
        try:
            timeline = TimelineModel(
                year=request.year,
                title=request.title,
                body=request.body,
                sort_order=request.sort_order,
            )

            timeline_id = self.timeline_repo.create(timeline)

            self.db.commit()

            return timeline_id

        except:
            self.db.rollback()
            raise

    """
    年表を更新する
    """

    def update_timeline(self, timeline_id: int, request: TimelinePutRequest) -> None:
        try:
            if not self.timeline_repo.exist_check(timeline_id):
                raise ApplicationError(
                    message=ErrorMessage.TIMELINE_NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            self.timeline_repo.update(
                timeline_id,
                request.year,
                request.title,
                request.body,
                request.sort_order,
            )

            self.db.commit()

        except:
            self.db.rollback()
            raise

    """
    年表を削除する
    """

    def delete_timeline(self, timeline_id: int) -> None:
        try:
            if not self.timeline_repo.exist_check(timeline_id):
                raise ApplicationError(
                    message=ErrorMessage.TIMELINE_NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            self.timeline_repo.delete(timeline_id)

            self.db.commit()

        except:
            self.db.rollback()
            raise
