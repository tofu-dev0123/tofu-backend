from fastapi import APIRouter, Depends
from app.api.deps import get_public_about_service
from app.schemas.profile import AboutResponse
from app.services.public.about_service import PublicAboutService


router = APIRouter(prefix="/about", tags=["About 公開About関連"])


@router.get("", response_model=AboutResponse)
def get_about(
    service: PublicAboutService = Depends(get_public_about_service),
):
    return service.get_about()
