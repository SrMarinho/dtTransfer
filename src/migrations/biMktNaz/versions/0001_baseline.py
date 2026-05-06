"""baseline

Revision ID: 0001
Revises:
Create Date: 2026-04-30

"""
from alembic import op
from pathlib import Path

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    sql_file = Path(__file__).parent / "0001_baseline.sql"
    if sql_file.exists():
        op.execute(sql_file.read_text(encoding="utf-8"))


def downgrade() -> None:
    pass
