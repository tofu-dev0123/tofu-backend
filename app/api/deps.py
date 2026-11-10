from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.account_service import AccountService
from app.services.auth_service import AuthService
from app.services.image_service import ImageService
from app.services.post_service import PostService
from app.services.product_service import ProductService
from app.services.profile_service import ProfileService
from app.services.timeline_service import TimelineService
from app.services.public.about_service import PublicAboutService
from app.services.public.post_service import PublicPostService
from app.services.public.product_service import PublicProductService


# ==================== 管理者用 ====================


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_image_service(db: Session = Depends(get_db)) -> ImageService:
    return ImageService(db)


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


def get_timeline_service(db: Session = Depends(get_db)) -> TimelineService:
    return TimelineService(db)


# ==================== 公開用 ====================


def get_public_about_service(db: Session = Depends(get_db)) -> PublicAboutService:
    return PublicAboutService(db)


def get_public_post_service(db: Session = Depends(get_db)) -> PublicPostService:
    return PublicPostService(db)


def get_public_product_service(
    db: Session = Depends(get_db),
) -> PublicProductService:
    return PublicProductService(db)
