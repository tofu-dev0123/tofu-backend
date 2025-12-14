from pydantic import BaseModel, Field

class Image(BaseModel):
    image_id: int = Field(..., description="画像ID")
    url: str = Field(..., description="画像URL")
    alt_text:str | None = Field(None, description="代替テキスト")