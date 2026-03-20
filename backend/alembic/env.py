"""Alembic environment configuration for async SQLAlchemy."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings

# Alembic Config object
config = context.config

# Override sqlalchemy.url from app settings
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import ALL models so Alembic detects them ────────────────────
from app.database import Base  # noqa: E402

from app.modules.projects.models import *  # noqa: F401, F403, E402
from app.modules.estimates.models import *  # noqa: F401, F403, E402
from app.modules.contracts.models import *  # noqa: F401, F403, E402
from app.modules.drawings.models import *  # noqa: F401, F403, E402
from app.modules.documents.models import *  # noqa: F401, F403, E402
from app.modules.progress.models import *  # noqa: F401, F403, E402
from app.modules.asbuilt.models import *  # noqa: F401, F403, E402
from app.modules.materials.models import *  # noqa: F401, F403, E402
from app.modules.inspections.models import *  # noqa: F401, F403, E402
from app.modules.reports.models import *  # noqa: F401, F403, E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode (async)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
