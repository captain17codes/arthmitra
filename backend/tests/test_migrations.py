"""
Verify Alembic migrations up and down cleanly.
"""

import os
from alembic import command
from alembic.config import Config


def test_alembic_migrations_up_and_down(tmp_path):
    db_file = tmp_path / "test_migration.db"
    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ini_path = os.path.join(backend_dir, "alembic.ini")
    migrations_dir = os.path.join(backend_dir, "migrations")

    config = Config(ini_path)
    config.set_main_option("sqlalchemy.url", db_url)
    config.set_main_option("script_location", migrations_dir)

    # 1. Upgrade to head
    command.upgrade(config, "head")

    # 2. Downgrade to base
    command.downgrade(config, "base")

    # 3. Upgrade to head again (idempotent re-run)
    command.upgrade(config, "head")
