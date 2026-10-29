"""Self-service accounts: citizen role, OTP codes, phone hash and PIN lockout.

Revision ID: 003_self_service_auth
Revises: 002_beneficiary_income
"""

import sqlalchemy as sa
from alembic import op

revision = "003_self_service_auth"
down_revision = "002_beneficiary_income"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'CITIZEN'")
            op.execute("ALTER TYPE orgtype ADD VALUE IF NOT EXISTS 'INDIVIDUAL'")
    op.add_column("users", sa.Column("phone_hash", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("failed_pin_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_phone_hash", "users", ["phone_hash"])
    op.create_table(
        "otp_codes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("phone_hash", sa.String(64), nullable=False, index=True),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("otp_codes")
    op.drop_index("ix_users_phone_hash", "users")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_pin_attempts")
    op.drop_column("users", "phone_hash")
