from pydantic import BaseModel, Field
from app.common.constant import Constant



class Image(BaseModel):
    image_id: int = Field(..., description="画像ID")
    url: str = Field(..., description="画像URL")
    alt_text: str | None = Field(None, description="代替テキスト")

    
class ImageUploadResponse(BaseModel):
    """画像アップロード成功レスポンススキーマ"""

    image_id: int = Field(..., description="画像ID")
    url: str = Field(..., description="画像URL")
    alt_text: str = Field(..., description="代替テキスト")
