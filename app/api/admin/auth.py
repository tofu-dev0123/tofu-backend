from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import login_service
from app.schemas.auth import LoginRequest, LoginResponse
from app.core.security import LoginFailError
from app.core.message import Message, ErrorMessage

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        # 認証処理を行いtokenを取得する
        token = login_service(request.username, request.password, db)

        return LoginResponse(
            message=Message.LOGIN_SUCCESS,
            token=token
        )
    
    except LoginFailError:
        # カスタムハンドラーへバトン渡し
        raise
    
    except Exception:
        # その他の予期しないエラー（500エラー）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_SERVER_ERROR
        )

