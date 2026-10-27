from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import admin, advisory, auth, beneficiaries, cases, dashboard, dpr, geo, meta, speech


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions: ensure database tables & baseline seed exist
    from .database import Base, async_session_maker, engine
    from .seed import seed_all
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_session_maker() as session:
            await seed_all(session)
    except Exception as e:
        print(f"Startup DB init notice: {e}")
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
