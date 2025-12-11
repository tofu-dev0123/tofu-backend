from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Alembic Config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------------------
#  モデル定義を強制ロード（最重要ポイント）
# -----------------------------------------
import app.models.user  # noqa: F401
import app.models.post  # noqa: F401
import app.models.tag  # noqa: F401
import app.models.post_tag  # noqa: F401
import app.models.image  # noqa: F401

# Base を読み込む（model import の後にするのが安全）
from app.db.base_class import Base

target_metadata = Base.metadata
# -----------------------------------------


def get_url():
    from app.core.config import settings

    return settings.database_url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
