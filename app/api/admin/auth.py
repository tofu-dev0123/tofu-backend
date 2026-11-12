from fastapi import APIRouter, Depends
from app.api.deps import get_auth_service
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, MeResponse
from app.core.security import get_current_user
from app.common.message import Message

router = APIRouter(prefix="/auth", tags=["Auth 認証機能"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    # 認証処理を行いtokenを取得する
    token = service.login(request.username, request.password)

    return LoginResponse(message=Message.LOGIN_SUCCESS, token=token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user),
) -> LogoutResponse:

    return LogoutResponse(message=Message.LOGOUT_SUCCESS)


@router.post("/me", response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        account_name=current_user.account_name,
    )
