from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import UserRole
from models.governance import AuditLog, ProcessingLog
from models.organization import User

from .database import get_db
from .security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]
AuthToken = Annotated[HTTPAuthorizationCredentials | None, Security(security_scheme)]


async def get_current_user(
    db: DbSession,
    auth: AuthToken,
) -> User:
    """Validate Bearer token and return active authenticated user."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(auth.credentials)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["user_id"])
    res = await db.execute(select(User).where(User.id == user_id, User.active == True))  # noqa: E712
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(allowed_roles: list[UserRole]):
    """Enforce role-based access control (RBAC)."""
    async def role_checker(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{user.role.value}' lacks required permissions",
            )
        return user
    return role_checker


async def log_audit(
    db: AsyncSession,
    actor_id: int | None,
    action: str,
    entity: str,
    entity_id: str,
    diff: dict[str, Any] | None = None,
) -> None:
    """Create audit trail record for state-changing operations."""
    log_entry = AuditLog(
        actor_id=actor_id,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        diff=diff,
    )
    db.add(log_entry)


async def log_processing(
    db: AsyncSession,
    actor_id: int | None,
    purpose: str,
    entity: str,
    entity_id: str,
) -> None:
    """Create DPDP Act processing log for read/access of beneficiary personal data."""
    proc_entry = ProcessingLog(
        actor_id=actor_id,
        purpose=purpose,
        entity=entity,
        entity_id=str(entity_id),
    )
    db.add(proc_entry)
