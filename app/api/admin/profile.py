from fastapi import APIRouter, Depends
from app.api.deps import get_profile_service
from app.core.security import get_current_user
from app.common.message import Message
from app.schemas.profile import (
    ProfileResponse,
    ProfilePutRequest,
    ProfilePutResponse,
)
from app.services.profile_service import ProfileService
from app.models.user import User


router = APIRouter(prefix="/profile", tags=["Profile プロフィール関連"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_profile()


@router.put("", response_model=ProfilePutResponse)
async def update_profile(
    request: ProfilePutRequest,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
):
    service.update_profile(request)

    return ProfilePutResponse(message=Message.PROFILE_UPDATE_SUCCESS)
