from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class OtpCode(Base):
    """One-time password sent by SMS. Only hashes are stored."""

    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_hash = Column(String(64), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
