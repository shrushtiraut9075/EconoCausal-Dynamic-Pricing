"""FastAPI main application entry point.

Implements PROJECT.md §8 API contract.
All endpoints use pydantic v2 schemas and return structured errors:
  {error: {code, message, details}}
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from econocausal import __version__
from econocausal.api.routes import datasets, intelligence, models, monitor, optimize
from econocausal.config import settings
from econocausal.logging import configure_logging, get_logger

configure_logging(log_level=settings.log_level, log_format=settings.log_format)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: setup and teardown."""
    settings.ensure_dirs()
    logger.info(
        "EconoCausal API starting",
        version=__version__,
        host=settings.api_host,
        port=settings.api_port,
    )
    yield
    logger.info("EconoCausal API shutting down")


app = FastAPI(
    title="EconoCausal API",
    description=(
        "Causal-AI dynamic pricing engine. "
        "Estimates individual treatment effects via Double ML and allocates "
        "a fixed marketing budget to maximise incremental profit."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: object) -> Response:
    """Add X-Process-Time header to all responses."""
    start = time.perf_counter()
    response = await call_next(request)  # type: ignore[operator]
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    return response


# ── Health endpoint ───────────────────────────────────────────────────────────
@app.get(
    "/health",
    summary="Liveness probe",
    tags=["System"],
    response_model=dict[str, str],
)
async def health() -> dict[str, str]:
    """Return API version and status for liveness checks."""
    return {"status": "ok", "version": __version__}


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(optimize.router, prefix="", tags=["Optimisation"])
app.include_router(monitor.router, prefix="/monitor", tags=["Monitoring"])
app.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])

# Mount under /api prefix as well for seamless frontend routing
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(models.router, prefix="/api/models", tags=["Models"])
app.include_router(optimize.router, prefix="/api", tags=["Optimisation"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["Monitoring"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["Intelligence"])


@app.get("/api/health", tags=["System"], response_model=dict[str, str], include_in_schema=False)
async def api_health() -> dict[str, str]:
    """Return API version and status under /api/health."""
    return {"status": "ok", "version": __version__}


# ── Frontend SPA Serving (for Unified Single-Service Deployment) ─────────────
frontend_dist = Path(__file__).resolve().parents[4] / "frontend" / "dist"
if frontend_dist.is_dir() and (frontend_dist / "index.html").is_file():
    if (frontend_dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return structured error for unhandled exceptions."""
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": str(exc),
            }
        },
    )
