import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import INSECURE_DEFAULT_SECRET, settings
from .routers import admin, advisory, auth, beneficiaries, cases, dashboard, dpr, geo, meta, speech


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == "production":
        if settings.secret_key == INSECURE_DEFAULT_SECRET:
            print("CRITICAL: SECRET_KEY is the insecure default in production. Set SECRET_KEY now.")
        if settings.debug:
            print("WARNING: DEBUG=true in production.")

    # Startup actions: enable extensions, ensure tables & baseline seed exist
    from sqlalchemy import text

    from models import spatial

    from .database import Base, async_session_maker, engine
    from .seed import seed_all

    if engine.dialect.name == "postgresql":
        for ext in ("postgis", "pg_trgm"):
            try:
                async with engine.begin() as conn:
                    await conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext}"))
                if ext == "postgis":
                    spatial.POSTGIS_ENABLED = True
            except Exception as e:  # extension not installed on this server
                print(f"WARNING: could not enable extension {ext}: {e}")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            if engine.dialect.name == "postgresql":
                # create_all does not add columns to existing tables; keep this list in sync
                # with Alembic migrations until deploys run `alembic upgrade head`.
                await conn.execute(
                    text("ALTER TABLE beneficiaries ADD COLUMN IF NOT EXISTS annual_family_income INTEGER")
                )
        async with async_session_maker() as session:
            await seed_all(session)
        if os.getenv("SEED_DEMO_DATA", "").lower() == "true":
            from seed_demo import init_and_seed_database

            await init_and_seed_database()
    except Exception as e:
        print(f"FATAL: database initialisation failed: {e!r}")
        if settings.environment == "production":
            raise  # fail the deploy loudly instead of serving 500s
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.app_name,
    description="ArthMitra: Production AI-assisted hyper-local business advisory & financial structuring",
    version="1.0.0",
    lifespan=lifespan,
)

class _TrailingSlashMiddleware:
    """
    Serve '/cases/' as '/cases' (and vice versa) in place, instead of a 307 redirect.
    Behind the Vercel proxy a redirect points the browser at another origin and the
    Authorization header is dropped, which logged agents straight back out.
    """

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            if path != "/" and not self._matches(scope):
                alt = path.rstrip("/") if path.endswith("/") else path + "/"
                alt_scope = {**scope, "path": alt, "raw_path": alt.encode()}
                if self._matches(alt_scope):
                    scope = alt_scope
        await self.asgi_app(scope, receive, send)

    @staticmethod
    def _matches(scope) -> bool:
        from starlette.routing import Match

        return any(r.matches(scope)[0] == Match.FULL for r in app.router.routes)


_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    # Auth uses bearer tokens (no cookies), so credentials are never needed cross-origin.
    allow_origins=_cors_origins or ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(_TrailingSlashMiddleware)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.include_router(geo.router)
app.include_router(auth.router)
app.include_router(meta.router)
app.include_router(beneficiaries.router)
app.include_router(cases.router)
app.include_router(dashboard.router)
app.include_router(advisory.router)
app.include_router(dpr.router)
app.include_router(speech.router)
app.include_router(admin.router)


@app.get("/health", tags=["Health"])
async def root_health():
    """Root health check required by TECH_SPEC §1."""
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}


@app.get(f"{settings.api_prefix}/health", tags=["Health"])
async def api_health():
    """API namespace health check."""
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}
