from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import geo


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
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

app.include_router(geo.router)


@app.get("/health", tags=["Health"])
async def root_health():
    """Root health check required by TECH_SPEC §1."""
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}


@app.get(f"{settings.api_prefix}/health", tags=["Health"])
async def api_health():
    """API namespace health check."""
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}
