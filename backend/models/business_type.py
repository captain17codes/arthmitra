from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base

from .enums import BenchmarkConfidence, BusinessSector


class BusinessType(Base):
    __tablename__ = "business_types"

    code = Column(String(50), primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_mr = Column(String(255), nullable=False)
    name_hi = Column(String(255), nullable=False)
    sector = Column(Enum(BusinessSector), nullable=False)
    hces_category = Column(String(100), nullable=False)
    decay_lambda = Column(Float, nullable=False, default=0.18)
    icon = Column(String(100), nullable=True)

    benchmarks = relationship("Benchmark", back_populates="business_type", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="business_type")


class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_code = Column(String(50), ForeignKey("business_types.code", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(Numeric(14, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    region = Column(String(100), nullable=False)
    source_title = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    source_year = Column(Integer, nullable=False)
    confidence = Column(Enum(BenchmarkConfidence), nullable=False, default=BenchmarkConfidence.OFFICIAL)
    version = Column(String(50), nullable=False, default="1.0.0")
    active = Column(Boolean, nullable=False, default=True)

    business_type = relationship("BusinessType", back_populates="benchmarks")
