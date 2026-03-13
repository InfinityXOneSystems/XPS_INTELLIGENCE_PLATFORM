from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from apps.backend.api.router import api_router
from apps.backend.core.config import settings
from apps.backend.core.database import connect_db, disconnect_db
from apps.backend.core.logging import configure_logging
from apps.backend.core.redis_client import connect_redis, disconnect_redis

configure_logging(level=settings.LOG_LEVEL)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", service="xps-backend")
    await connect_db()
    await connect_redis()
    yield
    logger.info("shutdown", service="xps-backend")
    await disconnect_db()
    await disconnect_redis()


app = FastAPI(
    title="XPS Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning("validation_error", path=request.url.path, errors=exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception", path=request.url.path, error=str(exc), exc_info=True
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "xps-backend", "version": "1.0.0"}


app.include_router(api_router, prefix="/api/v1")
