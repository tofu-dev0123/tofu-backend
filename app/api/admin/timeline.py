from fastapi import APIRouter, Depends, Path
from app.api.deps import get_timeline_service
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
from app.common.constant import Constant


router = APIRouter(prefix="/timelines", tags=["Timeline 年表関連"])


@router.get("", response_model=TimelineListResponse)
async def get_timelines(
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
) -> TimelineListResponse:
    return service.get_timelines()


@router.post("", response_model=TimelineResponse)
async def create_timeline(
    request: TimelinePostRequest,
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
) -> TimelineResponse:
    timeline_id = service.create_timeline(request)

    return TimelineResponse(
        message=Message.TIMELINE_CREATE_SUCCESS, timeline_id=timeline_id
    )


@router.put("/{timeline_id}", response_model=TimelineResponse)
async def update_timeline(
    request: TimelinePutRequest,
    timeline_id: int = Path(..., ge=Constant.MIN_TIMELINE_ID, description="年表ID"),
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
) -> TimelineResponse:
    service.update_timeline(timeline_id, request)

    return TimelineResponse(
        message=Message.TIMELINE_UPDATE_SUCCESS, timeline_id=timeline_id
    )


@router.delete("/{timeline_id}", response_model=TimelineDeleteResponse)
async def delete_timeline(
    timeline_id: int = Path(..., ge=Constant.MIN_TIMELINE_ID, description="年表ID"),
    service: TimelineService = Depends(get_timeline_service),
    current_user: User = Depends(get_current_user),
) -> TimelineDeleteResponse:
    service.delete_timeline(timeline_id)

    return TimelineDeleteResponse(message=Message.TIMELINE_DELETE_SUCCESS)
