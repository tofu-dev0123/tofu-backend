from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, ErrorResponse, ErrorDetail
from app.core.security import create_access_token, verify_password, ValidationError, LoginFailError

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    ログインエンドポイント
    
    1. 入力値をチェックする
    2. usersテーブルからusernameをキーにユーザー情報を取得する
    3. パスワードを照合する
    4. JWTトークンを生成する
    5. 200でレスポンスを返却する
    """
    try:
        # 1. 入力値バリデーション
        validation_errors = []
        
        if not request.username or not request.username.strip():
            validation_errors.append(
                ErrorDetail(value="username", message="ユーザー名は必須項目です")
            )
        
        if not request.password or not request.password.strip():
            validation_errors.append(
                ErrorDetail(value="password", message="パスワードは必須項目です")
            )
        
        if validation_errors:
            raise ValidationError(
                message="",
                details=validation_errors
            )
        
        # 2. ユーザー情報を取得
        try:
            user = db.query(User).filter(User.username == request.username).first()
        except SQLAlchemyError as e:
            # DB起因のエラー
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="データベースエラーが発生しました"
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
            message="ログインに成功しました",
            token=token
        )
    
    except ValidationError as e:
        # 400（バリデーションエラー）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                message=e.message,
                error="VALIDATION_ERROR",
                details=e.details
            ).dict()
        )
    
    except LoginFailError as e:
        # 400（ログインエラー）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                message=e.message,
                error="LOGIN_FAIL",
                details=[]
            ).dict()
        )
    
    except HTTPException:
        # 既にHTTPExceptionの場合はそのまま再発生
        raise
    
    except Exception as e:
        # その他の予期しないエラー（500エラー）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )

