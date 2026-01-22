from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, MeResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.core.exceptions.auth_exceptions import LoginFailError
from app.common.message import Message, ErrorMessage

router = APIRouter(prefix="/auth", tags=["Auth 認証機能"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        # 認証処理を行いtokenを取得する
        token = service.login(request.username, request.password)

    except LoginFailError as e:
        # カスタムハンドラーへバトン渡し
        raise e

    except Exception:
        # その他の予期しないエラー（500エラー）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_SERVER_ERROR,
        )

    # クッキーにトークンを設定
    response.set_cookie(
        key="auth_token",
        value=token,
        max_age=int(timedelta(hours=3).total_seconds()),
        domain=".tofubase.com",
        secure=True,
        httponly=True,
        samesite="none",
    )

    return LoginResponse(message=Message.LOGIN_SUCCESS, token=token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    current_user=Depends(get_current_user),
):
    # クッキーを削除
    response.delete_cookie(
        key="auth_token",
        domain=settings.cookie_domain,
        secure=settings.cookie_secure,
        httponly=settings.COOKIE_HTTP_ONLY,
        samesite=settings.COOKIE_SAME_SITE,
    )

    return LogoutResponse(message=Message.LOGOUT_SUCCESS)


@router.post("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        account_name=current_user.account_name,
    )
