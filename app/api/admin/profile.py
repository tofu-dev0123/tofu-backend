from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
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


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


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
