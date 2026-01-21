from pydantic import BaseModel, Field


class Tag(BaseModel):
    tag_id: int = Field(..., description="タグID")
    name: str = Field(..., description="タグ名")
    slug: str = Field(..., description="タグスラグ")
