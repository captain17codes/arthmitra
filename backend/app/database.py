from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg does not understand libpq's ?sslmode=/channel_binding= (Neon, Supabase URLs).
connect_args: dict = {}
_parts = urlsplit(db_url)
if _parts.query:
    _q = dict(parse_qsl(_parts.query))
    _ssl = _q.pop("sslmode", None)
    _q.pop("channel_binding", None)
    if _ssl and _ssl not in ("disable", "allow"):
        connect_args["ssl"] = "require"
    db_url = urlunsplit(_parts._replace(query=urlencode(_q)))

_engine_kwargs: dict = {"echo": settings.debug, "future": True}
if db_url.startswith("postgresql"):
    # Serverless Postgres (e.g. Neon) closes idle connections; check before use.
    _engine_kwargs.update(pool_pre_ping=True, pool_recycle=300, connect_args=connect_args)

engine = create_async_engine(db_url, **_engine_kwargs)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
