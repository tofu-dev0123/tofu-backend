"""fix invalid slugs on published posts

Revision ID: e5f4a7b3c9d1
Revises: d4e3f6a9b2c8
Create Date: 2026-09-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op  # pyright: ignore[reportAttributeAccessIssue]
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f4a7b3c9d1'
down_revision: Union[str, None] = 'd4e3f6a9b2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# d4e3f6a9b2c8 で対象外とした公開済み記事の不正スラグ。
# タイトルから生成したスラグへ個別に振り直す (Issue #96)。
SLUG_FIXES = {
    # 【Shelfie】DevLog #05 | Clerk から独自 OAuth プロバイダへ移行した話
    "error-500-server-error-1500-thats-an-error-there-w":
        "shelfie-devlog-05-story-of-migrating-from-clerk-to",
    # ループエンジニアリングを実践してみた
    "error-500-server-error-1500-thats-an-error-there-w-1":
        "i-tried-loop-engineering",
    # 【検索処理】転置インデックスについて
    "error-500-server-error-1500-thats-an-error-there-w-2":
        "search-processing-about-inverted-index",
}


def _rename_slugs(mapping: dict[str, str]) -> None:
    conn = op.get_bind()

    for before, after in mapping.items():
        # 対象が無い場合は既に是正済みとしてスキップする
        target = conn.execute(
            sa.text("SELECT 1 FROM posts WHERE slug = :slug"), {"slug": before}
        ).first()

        if target is None:
            continue

        # 変更先が使われている場合は unique 制約違反になるため中断する
        conflict = conn.execute(
            sa.text("SELECT 1 FROM posts WHERE slug = :slug"), {"slug": after}
        ).first()

        if conflict is not None:
            raise RuntimeError(f"slug '{after}' は既に使用されています")

        conn.execute(
            sa.text("UPDATE posts SET slug = :after WHERE slug = :before"),
            {"after": after, "before": before},
        )


def upgrade() -> None:
    _rename_slugs(SLUG_FIXES)


def downgrade() -> None:
    _rename_slugs({after: before for before, after in SLUG_FIXES.items()})
