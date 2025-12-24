from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, MeResponse
from app.core.config import Settings
from app.core.security import get_current_user
from app.core.exceptions.auth_exceptions import LoginFailError
from app.common.message import Message, ErrorMessage

router = APIRouter(prefix="/auth", tags=["Auth 認証機能"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        # 認証処理を行いtokenを取得する
        token = service.login(request.username, request.password)
        
        # Cookie に JWT をセット
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=not Settings.is_local,                # local は False / prod は True
            samesite="none" if not Settings.is_local else "lax",
            max_age=60 * 60,
            path="/",
        )

    except LoginFailError as e:
        # カスタムハンドラーへバトン渡し
        raise e

    except Exception:
        # その他の予期しないエラー（500エラー）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_SERVER_ERROR,
        )

    return LoginResponse(message=Message.LOGIN_SUCCESS, token=token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response, current_user=Depends(get_current_user)):
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    return LogoutResponse(message=Message.LOGOUT_SUCCESS)


@router.post("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        account_name=current_user.account_name,
    )
