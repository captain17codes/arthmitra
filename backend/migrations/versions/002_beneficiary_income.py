"""Add exact annual family income to beneficiaries.

Revision ID: 002_beneficiary_income
Revises: 001_initial_schema
"""

import sqlalchemy as sa
from alembic import op

revision = "002_beneficiary_income"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("beneficiaries", sa.Column("annual_family_income", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("beneficiaries", "annual_family_income")
