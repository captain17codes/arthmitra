from __future__ import annotations

from typing import Any
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base
from .enums import CaseStatus, InputSource


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True)
    village_lgd = Column(Integer, ForeignKey("villages.lgd_code"), nullable=False, index=True)
    business_code = Column(String(50), ForeignKey("business_types.code"), nullable=False, index=True)

    margin_available = Column(Numeric(14, 2), nullable=False)
    target_project_cost = Column(Numeric(14, 2), nullable=True)
    language = Column(String(10), nullable=False, default="mr")

    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.DRAFT, index=True)
    status_reason_code = Column(String(100), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    beneficiary = relationship("Beneficiary", back_populates="cases")
    village = relationship("Village", back_populates="cases")
    business_type = relationship("BusinessType", back_populates="cases")
    created_by_user = relationship("User", back_populates="created_cases")

    inputs = relationship("CaseInput", back_populates="case", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="case", cascade="all, delete-orphan")

    __table_args__: Any = (
        Index("ix_cases_status_created_by", "status", "created_by"),
    )


class CaseInput(Base):
    __tablename__ = "case_inputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    source = Column(Enum(InputSource), nullable=False, default=InputSource.AGENT)
    transcript = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case = relationship("Case", back_populates="inputs")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    engine_version = Column(String(50), nullable=False)
    scheme_versions = Column(JSON, nullable=False)  # JSONB
    benchmarks_version = Column(String(50), nullable=False)
    input_snapshot = Column(JSON, nullable=False)
    output = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case = relationship("Case", back_populates="evaluations")
    advisories = relationship("Advisory", back_populates="evaluation", cascade="all, delete-orphan")
    dpr_documents = relationship("DprDocument", back_populates="evaluation", cascade="all, delete-orphan")


class Advisory(Base):
    __tablename__ = "advisories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, default="mr")
    model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=False)
    output = Column(JSON, nullable=False)
    validator_passed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    evaluation = relationship("Evaluation", back_populates="advisories")


class DprDocument(Base):
    __tablename__ = "dpr_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False)
    object_key = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    evaluation = relationship("Evaluation", back_populates="dpr_documents")
