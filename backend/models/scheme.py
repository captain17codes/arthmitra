from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

from .enums import SchemeStatus


class Scheme(Base):
    __tablename__ = "schemes"

    code = Column(String(50), primary_key=True)
    name_en = Column(String(255), nullable=False)
    name_mr = Column(String(255), nullable=False)
    agency = Column(String(255), nullable=False)
    channel = Column(String(255), nullable=False)
    portal_url = Column(String(500), nullable=True)

    versions = relationship("SchemeVersion", back_populates="scheme", cascade="all, delete-orphan")


class SchemeVersion(Base):
    __tablename__ = "scheme_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_code = Column(String(50), ForeignKey("schemes.code", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    status = Column(Enum(SchemeStatus), nullable=False, default=SchemeStatus.VERIFIED)
    rules_yaml = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    source_date = Column(String(50), nullable=True)
    effective_from = Column(String(50), nullable=True)
    published_by = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scheme = relationship("Scheme", back_populates="versions")
