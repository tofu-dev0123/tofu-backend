from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, MeResponse
from app.core.security import get_current_user
from app.core.exceptions.auth_exceptions import LoginFailError
from app.common.message import Message, ErrorMessage

router = APIRouter(prefix="/auth", tags=["Auth 認証機能"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    
    try:
        # 認証処理を行いtokenを取得する
        token = service.login_service(request.username, request.password, db)

    except LoginFailError:
        # カスタムハンドラーへバトン渡し
        raise

    except Exception:
        # その他の予期しないエラー（500エラー）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_SERVER_ERROR,
        )

    return LoginResponse(message=Message.LOGIN_SUCCESS, token=token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user=Depends(get_current_user)):
    return LogoutResponse(message=Message.LOGOUT_SUCCESS)


@router.post("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        account_name=current_user.account_name,
    )
