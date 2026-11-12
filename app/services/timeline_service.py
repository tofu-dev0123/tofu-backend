import logging
from sqlalchemy.orm import Session
from app.repositories.timeline_repository import TimelineRepository
from app.models.timeline import Timeline as TimelineModel
from app.schemas.timeline import (
    TimelineListResponse,
    TimelinePostRequest,
    TimelinePutRequest,
)
from app.common.message import ErrorMessage
from app.services.transaction import transaction
from app.services.guards import ensure_exists
from app.services.mappers import to_timeline

logger = logging.getLogger(__name__)


class TimelineService:

    def __init__(
        self,
        db: Session,
        timeline_repo: TimelineRepository | None = None,
    ) -> None:
        self.db = db
        self.timeline_repo = timeline_repo or TimelineRepository(db)

    """
    年表一覧を取得する
    """

    def get_timelines(self) -> TimelineListResponse:
        timelines = self.timeline_repo.find_all()

        timeline_list = [to_timeline(t) for t in timelines]

        return TimelineListResponse(timelines=timeline_list)

    """
    年表を作成する
    """

    def create_timeline(self, request: TimelinePostRequest) -> int:
        with transaction(self.db):
            timeline = TimelineModel(
                year=request.year,
                title=request.title,
                body=request.body,
                sort_order=request.sort_order,
            )

            timeline_id = self.timeline_repo.create(timeline)

        logger.info("timeline created", extra={"timeline_id": timeline_id})

        return timeline_id

    """
    年表を更新する
    """

    def update_timeline(self, timeline_id: int, request: TimelinePutRequest) -> None:
        with transaction(self.db):
            ensure_exists(
                self.timeline_repo.exists_by_id(timeline_id),
                ErrorMessage.TIMELINE_NOT_EXIST,
            )

            self.timeline_repo.update(
                timeline_id,
                request.year,
                request.title,
                request.body,
                request.sort_order,
            )

        logger.info("timeline updated", extra={"timeline_id": timeline_id})

    """
    年表を削除する
    """

    def delete_timeline(self, timeline_id: int) -> None:
        with transaction(self.db):
            ensure_exists(
                self.timeline_repo.exists_by_id(timeline_id),
                ErrorMessage.TIMELINE_NOT_EXIST,
            )

            self.timeline_repo.delete(timeline_id)

        logger.info("timeline deleted", extra={"timeline_id": timeline_id})
