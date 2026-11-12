"""add github_url to products

Revision ID: c3d2e5f8a1b7
Revises: b2f1a9c7d3e4
Create Date: 2026-07-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op  # pyright: ignore[reportAttributeAccessIssue]
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d2e5f8a1b7'
down_revision: Union[str, None] = 'b2f1a9c7d3e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('github_url', sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('products', 'github_url')
