from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    func,
)

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False)
    diff = Column(JSON, nullable=True)
    at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class ProcessingLog(Base):
    __tablename__ = "processing_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(Integer, nullable=True, index=True)
    purpose = Column(String(255), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class DeletionRequest(Base):
    __tablename__ = "deletion_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    beneficiary_id = Column(Integer, nullable=False, index=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    by = Column(Integer, nullable=False)
