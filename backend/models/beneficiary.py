from __future__ import annotations

from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.security import EncryptedString
from .enums import ConsentMethod, TriState


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # 🔒 Encrypted PII Column
    first_name = Column(EncryptedString(256), nullable=False)

    gender = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    category = Column(String(20), nullable=False)  # SC, ST, OBC, VJNT, SBC, General
    category_verified = Column(Boolean, nullable=False, default=False)
    disability_40 = Column(Boolean, nullable=False, default=False)
    occupation_flags = Column(JSON, nullable=True)  # list of str flags, e.g. ["sanitation_worker"]
    income_band = Column(String(50), nullable=False)
    education_band = Column(String(50), nullable=False)
    shg_member = Column(Boolean, nullable=False, default=False)

    prior_subsidy = Column(Enum(TriState), nullable=False, default=TriState.UNKNOWN)
    credit_default = Column(Enum(TriState), nullable=False, default=TriState.UNKNOWN)
    existing_emi_monthly = Column(Numeric(12, 2), nullable=False, default=0.0)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="beneficiaries")
    created_by_user = relationship("User", back_populates="created_beneficiaries")
    consents = relationship("Consent", back_populates="beneficiary", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="beneficiary", cascade="all, delete-orphan")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True)
    notice_version = Column(String(50), nullable=False)
    language = Column(String(10), nullable=False, default="mr")
    method = Column(Enum(ConsentMethod), nullable=False, default=ConsentMethod.VOICE)

    # 🔒 Encrypted Object Key for audio consent recording
    audio_object_key = Column(EncryptedString(512), nullable=True)
    audio_sha256 = Column(String(64), nullable=True)

    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    beneficiary = relationship("Beneficiary", back_populates="consents")
    agent = relationship("User", back_populates="recorded_consents")
