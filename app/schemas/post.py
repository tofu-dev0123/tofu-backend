from pydantic import BaseModel, Field, field_validator
from fastapi.exceptions import RequestValidationError
from typing import List, Literal
from app.common.constant import MAX_CONTENT_HTML_SIZE

class PostsPostRequest(BaseModel):
    """記事作成リクエストスキーマ"""
    
    title: str = Field(...,  max_length=255, description="タイトル")
    content_md: str = Field(..., description="マークダウン本文")
    content_html: str = Field(..., description="HTML本文")
    thumbnail_url: str | None = Field(None, max_length=500, description="サムネイル画像URL")
    status: Literal["DRAFT", "PUBLISHED"] = Field(..., description="公開ステータス")
    images: List[int] = Field(default_factory=list, description="画像IDの配列")
    tags: List[str] = Field(default_factory=list, description="タグの配列")
    
     # --- Validators ---

    @field_validator("content_md")
    def validate_content_md_size(cls, v):
        size = len(v.encode("utf-8"))
        if size > MAX_CONTENT_HTML_SIZE:
            raise RequestValidationError(
                [
                    {
                        "type": "size_over",
                        "loc": ("body", "content_md"),
                        "msg": "",
                        "input": v,
                    }
                ]
            )
        return v

    @field_validator("thumbnail_url")
    def empty_string_to_null(cls, v):
        if v == "":
            return None
        return v
    
    @field_validator("tags")
    def validate_tags(cls, v: List[str]) -> List[str]:
        # 個数制限（最大20件）
        if len(v) > 20:
            raise RequestValidationError(
                [
                    {
                        "type": "list_too_long",
                        "loc": ("body", "tags"),
                        "msg": "",
                        "input": v,
                    }
                ]
            )

        # 各要素の長さ制限（30文字以内）
        for tag in v:
            if len(tag) > 30:
                raise RequestValidationError(
                [
                    {
                        "type": "string_too_long",
                        "loc": ("body", "tags"),
                        "msg": "",
                        "input": v,
                    }
                ]
            )
        return v

class PostsPostResponse(BaseModel):
    """記事作成成功レスポンススキーマ"""

    message: str = Field(..., description="メッセージ")
    post_id: int = Field(..., description="記事ID")