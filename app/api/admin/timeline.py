from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import get_current_user
from app.common.message import Message
from app.schemas.timeline import (
    TimelineListResponse,
    TimelinePostRequest,
    TimelinePutRequest,
    TimelineResponse,
    TimelineDeleteResponse,
)
from app.services.timeline_service import TimelineService
from app.models.user import User


router = APIRouter(prefix="/timelines", tags=["Timeline 年表関連"])


def get_timeline_service(db: Session = Depends(get_db)) -> TimelineService:
    return TimelineService(db)


@router.get("", response_model=TimelineListResponse)
async def get_timelines(
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_timelines()


@router.post("", response_model=TimelineResponse)
async def create_timeline(
    request: TimelinePostRequest,
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
):
    timeline_id = service.create_timeline(request)

    return TimelineResponse(
        message=Message.TIMELINE_CREATE_SUCCESS, timeline_id=timeline_id
    )


@router.put("/{timeline_id}", response_model=TimelineResponse)
async def update_timeline(
    request: TimelinePutRequest,
    timeline_id: int = Path(..., ge=1, description="年表ID"),
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
):
    service.update_timeline(timeline_id, request)

    return TimelineResponse(
        message=Message.TIMELINE_UPDATE_SUCCESS, timeline_id=timeline_id
    )


@router.delete("/{timeline_id}", response_model=TimelineDeleteResponse)
async def delete_timeline(
    timeline_id: int = Path(..., ge=1, description="年表ID"),
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
):
    service.delete_timeline(timeline_id)

    return TimelineDeleteResponse(message=Message.TIMELINE_DELETE_SUCCESS)
