"""
FastAPI application entry point.

Creates the app instance, registers routers, configures CORS, sets up
the lifespan (startup / shutdown), and registers global exception handlers.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import close_db, init_db

# Routers
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.reports import router as reports_router
from app.api.upload import router as upload_router

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated on_event startup/shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute startup tasks, yield, then execute shutdown tasks."""
    logger.info("Starting ValuAI backend (env=%s)", settings.ENVIRONMENT)

    # Startup: create tables if they don't exist (Alembic handles production)
    await init_db()
    logger.info("Database initialised.")

    yield

    # Shutdown
    await close_db()
    logger.info("ValuAI backend shut down cleanly.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    application = FastAPI(
        title="ValuAI — Business Valuation API",
        description=(
            "AI-powered business valuation platform. "
            "Upload company documents and receive a comprehensive valuation report."
        ),
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    # In development allow all origins; tighten in production via env var
    cors_origins = ["*"] if not settings.is_production else []
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # ── Routers ────────────────────────────────────────────────────────────
    application.include_router(auth_router)
    application.include_router(upload_router)
    application.include_router(reports_router)
    application.include_router(jobs_router)

    # ── Health check ───────────────────────────────────────────────────────
    @application.get(
        "/health",
        tags=["health"],
        summary="Health check — returns 200 when the service is running",
        response_model=dict,
    )
    async def health() -> dict:
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "timestamp": time.time(),
        }

    # ── Exception handlers ─────────────────────────────────────────────────
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Request validation error: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "body": exc.body,
            },
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected internal error occurred. Please try again."},
        )

    return application


app = create_app()
