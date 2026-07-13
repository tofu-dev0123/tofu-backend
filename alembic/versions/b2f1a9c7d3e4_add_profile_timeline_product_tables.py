"""add profile timeline product tables

Revision ID: b2f1a9c7d3e4
Revises: 89b1c657b829
Create Date: 2026-07-13 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op  # pyright: ignore[reportAttributeAccessIssue]
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f1a9c7d3e4'
down_revision: Union[str, None] = '89b1c657b829'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('profiles',
    sa.Column('profile_id', sa.BigInteger(), nullable=False),
    sa.Column('headline', sa.String(length=255), nullable=False),
    sa.Column('bio', sa.Text(), nullable=False),
    sa.Column('site_description', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('profile_id')
    )
    op.create_index(op.f('ix_profiles_profile_id'), 'profiles', ['profile_id'], unique=False)

    op.create_table('timelines',
    sa.Column('timeline_id', sa.BigInteger(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('timeline_id')
    )
    op.create_index(op.f('ix_timelines_timeline_id'), 'timelines', ['timeline_id'], unique=False)

    op.create_table('products',
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('link_url', sa.String(length=500), nullable=True),
    sa.Column('published', sa.Boolean(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.create_index(op.f('ix_products_product_id'), 'products', ['product_id'], unique=False)

    op.create_table('product_tags',
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('tag_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.tag_id'], ),
    sa.PrimaryKeyConstraint('product_id', 'tag_id')
    )

    # profile は単一レコード運用のため空の初期行を seed する
    op.execute(
        "INSERT INTO profiles (headline, bio, site_description, created_at, updated_at) "
        "VALUES ('', '', '', now(), now())"
    )


def downgrade() -> None:
    op.drop_table('product_tags')
    op.drop_index(op.f('ix_products_product_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_timelines_timeline_id'), table_name='timelines')
    op.drop_table('timelines')
    op.drop_index(op.f('ix_profiles_profile_id'), table_name='profiles')
    op.drop_table('profiles')
