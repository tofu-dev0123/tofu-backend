from fastapi import APIRouter, Depends
from app.api.deps import get_account_service
from app.services.account_service import AccountService
from app.models.user import User
from app.schemas.account import (
    UpdateAccountNameRequest,
    UpdateAccountNameResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ChangeEmailRequest,
    ChangeEmailResponse,
)
from app.core.security import get_current_user
from app.common.message import Message

router = APIRouter(prefix="/account", tags=["Account アカウント管理"])


@router.patch("", response_model=UpdateAccountNameResponse)
async def update_account_name(
    request: UpdateAccountNameRequest,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    """アカウント名を変更する"""
    updated_user = service.update_account_name(current_user, request.account_name)

    return UpdateAccountNameResponse(
        message=Message.ACCOUNT_UPDATE_SUCCESS,
        user_id=updated_user.user_id,
        account_name=updated_user.account_name,
    )


@router.patch("/password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    """パスワードを変更する"""
    service.change_password(
        current_user, request.current_password, request.new_password
    )

    return ChangePasswordResponse(message=Message.PASSWORD_CHANGE_SUCCESS)


@router.patch("/email", response_model=ChangeEmailResponse)
async def change_email(
    request: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    """メールアドレスを変更する"""
    updated_user = service.change_email(
        current_user, request.current_email, request.new_email, request.password
    )

    return ChangeEmailResponse(
        message=Message.EMAIL_CHANGE_SUCCESS,
        user_id=updated_user.user_id,
        username=updated_user.username,
    )
