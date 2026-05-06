"""initial

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sample",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.Text, nullable=True),
        sa.Column("criado_em", sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table("sample")
