"""FastAPI application entry point with lifespan — all routers connected."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine

# Import all routers
from app.modules.projects.router import router as projects_router
from app.modules.estimates.router import router as estimates_router
from app.modules.contracts.router import router as contracts_router
from app.modules.drawings.router import router as drawings_router
from app.modules.documents.router import router as documents_router
from app.modules.progress.router import router as progress_router
from app.modules.asbuilt.router import router as asbuilt_router
from app.modules.materials.router import router as materials_router
from app.modules.inspections.router import router as inspections_router
from app.modules.reports.router import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown hooks."""
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="СМР ПСД — Система управления документацией",
    description="Управление ПСД и ИД для строительно-монтажных работ (РФ)",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers under /api/v1
API_PREFIX = "/api/v1"

app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(estimates_router, prefix=API_PREFIX)
app.include_router(contracts_router, prefix=API_PREFIX)
app.include_router(drawings_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)
app.include_router(progress_router, prefix=API_PREFIX)
app.include_router(asbuilt_router, prefix=API_PREFIX)
app.include_router(materials_router, prefix=API_PREFIX)
app.include_router(inspections_router, prefix=API_PREFIX)
app.include_router(reports_router, prefix=API_PREFIX)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}
