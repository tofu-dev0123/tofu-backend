from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------
# Alembic Config
# ---------------------------------------------------------
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------
# 最重要：モデルを強制 import する
# app/models/__init__.py が以下のように import している前提
# User, Post, Tag, Image, PostTag...
# ---------------------------------------------------------
import app.models  # ← 全モデルをここで読み込む（必須）

# その後で Base を読み込む
from app.db.base_class import Base

# Alembic が読む metadata
target_metadata = Base.metadata


# ---------------------------------------------------------
# DB URL
# ---------------------------------------------------------
def get_url():
    from app.core.config import settings
    return settings.database_url


# ---------------------------------------------------------
def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
