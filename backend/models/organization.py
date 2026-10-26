from __future__ import annotations

from typing import List
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base
from app.security import EncryptedString
from .enums import OrgType, UserRole


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(OrgType), nullable=False, default=OrgType.OTHER)
    district_lgd = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    beneficiaries = relationship("Beneficiary", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.AGENT, index=True)
    name = Column(String(255), nullable=False)
    # 🔒 Phone encrypted via EncryptedString
    phone = Column(EncryptedString(256), nullable=False)
    pin_hash = Column(String(255), nullable=False)
    lang = Column(String(10), nullable=False, default="mr")
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="users")
    created_cases = relationship("Case", back_populates="created_by_user")
    created_beneficiaries = relationship("Beneficiary", back_populates="created_by_user")
    recorded_consents = relationship("Consent", back_populates="agent")
