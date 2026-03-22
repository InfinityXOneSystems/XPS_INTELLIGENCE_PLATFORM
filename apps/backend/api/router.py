from __future__ import annotations

from fastapi import APIRouter

from apps.backend.api.routes import (artifacts, autonomy, health, leads, llm,
                                     scraper)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(leads.router)
api_router.include_router(artifacts.router)
api_router.include_router(scraper.router)
api_router.include_router(autonomy.router)
api_router.include_router(llm.router)
