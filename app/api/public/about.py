from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.profile import AboutResponse
from app.services.public.about_service import PublicAboutService


router = APIRouter(prefix="/about", tags=["About 公開About関連"])


def get_about_service(db: Session = Depends(get_db)) -> PublicAboutService:
    return PublicAboutService(db)


@router.get("", response_model=AboutResponse)
def get_about(
    service: PublicAboutService = Depends(get_about_service),
):
    return service.get_about()
