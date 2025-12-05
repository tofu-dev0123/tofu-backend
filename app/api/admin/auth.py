from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.errors import ErrorResponse
from app.core.security import create_access_token, verify_password, LoginFailError
from app.core.message import Message, ErrorMessage

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    ログインエンドポイント1
    
    1. 入力値をチェックする
    2. usersテーブルからusernameをキーにユーザー情報を取得する
    3. パスワードを照合する
    4. JWTトークンを生成する
    5. 200でレスポンスを返却する
    """
    try:       
        # 2. ユーザー情報を取得
        try:
            user = db.query(User).filter(User.username == request.username).first()
        except SQLAlchemyError as e:
            # DB起因のエラー
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorMessage.INTERNAL_SERVER_ERROR
            )
        # ユーザーが存在しない場合
        if not user:
            raise LoginFailError()
        
        # 3. パスワードを照合
        if not verify_password(request.password, user.password):
            raise LoginFailError()
        
        # 4. JWTトークンを生成
        token = create_access_token(user.user_id, user.username)
        
        # 5. 200でレスポンスを返却
        return LoginResponse(
            message=Message.LOGIN_SUCCESS,
            token=token
        )
    
    except LoginFailError:
        # カスタムハンドラーへバトン渡し
        raise
    
    except Exception as e:
        # その他の予期しないエラー（500エラー）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_SERVER_ERROR
        )

