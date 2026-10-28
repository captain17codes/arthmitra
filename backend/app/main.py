import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import admin, advisory, auth, beneficiaries, cases, dashboard, dpr, geo, meta, speech


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
