"""Startup housekeeping for accounts (idempotent)."""

from __future__ import annotations

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.enums import OrgType, UserRole
from models.organization import Organization, User

from .config import settings
from .security import hash_pin, normalize_phone, phone_hash


async def finalize_accounts(session: AsyncSession) -> None:
    bind = session.get_bind()
    if bind.dialect.name == "postgresql":
        # Demo seed inserts explicit ids; move sequences past them so sign-ups don't collide.
        for table in ("organizations", "users"):
            await session.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"GREATEST((SELECT COALESCE(MAX(id), 0) FROM {table}), 1))"
            ))

    # The product is self-service now: agent / supervisor logins are retired.
    await session.execute(
        update(User).where(User.role.in_([UserRole.AGENT, UserRole.SUPERVISOR])).values(active=False)
    )

    # Retire the old public demo admin (PIN was published in the README) unless re-claimed via env.
    demo_admin_phone = "9000000000"
    if normalize_phone(settings.admin_phone) != demo_admin_phone:
        await session.execute(
            update(User).where(User.role == UserRole.ADMIN, User.phone_hash == phone_hash(demo_admin_phone))
            .values(active=False)
        )
        for u in (await session.execute(select(User).where(User.role == UserRole.ADMIN, User.active == True))).scalars().all():  # noqa: E712
            if normalize_phone(u.phone or "") == demo_admin_phone:
                u.active = False

    for u in (await session.execute(select(User).where(User.phone_hash.is_(None)))).scalars().all():
        p = normalize_phone(u.phone or "")
        if p:
            u.phone_hash = phone_hash(p)

    admin_phone = normalize_phone(settings.admin_phone)
    if admin_phone and settings.admin_pin:
        ph = phone_hash(admin_phone)
        admin = (await session.execute(select(User).where(User.phone_hash == ph))).scalars().first()
        if admin is None:
            org = Organization(name="ArthMitra Administration", type=OrgType.OTHER)
            session.add(org)
            await session.flush()
            admin = User(org_id=org.id, role=UserRole.ADMIN, name="ArthMitra Admin", phone=admin_phone,
                         phone_hash=ph, pin_hash=hash_pin(settings.admin_pin), lang="en")
            session.add(admin)
        else:
            admin.role = UserRole.ADMIN
            admin.active = True
            admin.pin_hash = hash_pin(settings.admin_pin)
    await session.commit()
