"""fix invalid slugs generated from translation error pages

Revision ID: d4e3f6a9b2c8
Revises: c3d2e5f8a1b7
Create Date: 2026-09-11 00:00:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op  # pyright: ignore[reportAttributeAccessIssue]
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e3f6a9b2c8'
down_revision: Union[str, None] = 'c3d2e5f8a1b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 翻訳失敗時に保存されてしまった不正なスラグの条件
INVALID_SLUG_CONDITION = (
    "slug LIKE 'error-500%' OR slug LIKE 'that-s-an-error%' OR slug = ''"
)


def upgrade() -> None:
    """不正なスラグを UUID ベースのスラグへ振り直す

    下書き記事とタグのみを対象とする。公開済み記事は公開 URL が変わるため
    自動では変更しない（Issue #96 の方針に従い個別に対応する）。
    """
    conn = op.get_bind()

    # 下書き記事: 公開時にタイトルベースのスラグへ再生成される
    draft_post_ids = conn.execute(
        sa.text(
            f"SELECT post_id FROM posts WHERE status = 'DRAFT' AND ({INVALID_SLUG_CONDITION})"
        )
    ).scalars().all()

    for post_id in draft_post_ids:
        conn.execute(
            sa.text("UPDATE posts SET slug = :slug WHERE post_id = :post_id"),
            {"slug": f"draft-{uuid.uuid4().hex[:8]}", "post_id": post_id},
        )

    # タグ: 再生成の経路が無いため UUID ベースのスラグで固定する
    tag_ids = conn.execute(
        sa.text(f"SELECT tag_id FROM tags WHERE {INVALID_SLUG_CONDITION}")
    ).scalars().all()

    for tag_id in tag_ids:
        conn.execute(
            sa.text("UPDATE tags SET slug = :slug WHERE tag_id = :tag_id"),
            {"slug": f"tag-{uuid.uuid4().hex[:8]}", "tag_id": tag_id},
        )


def downgrade() -> None:
    # 不正な値へ戻す意味が無いため何もしない
    pass
