from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.backend.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])


class ChatRequest(BaseModel):
    messages: list[dict[str, Any]]
    model: str = ""


class ChatResponse(BaseModel):
    response: str
    provider: str


@router.get("/providers")
async def list_providers():
    providers = []
    if settings.GROQ_API_KEY:
        providers.append({"name": "groq", "available": True})
    providers.append({"name": "echo", "available": True})
    return {"providers": providers, "primary": settings.LLM_PROVIDER}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=422, detail="messages must not be empty")

    if settings.GROQ_API_KEY:
        return await _call_groq(request)

    return _echo_response(request)


async def _call_groq(request: ChatRequest) -> ChatResponse:
    try:
        import groq as groq_sdk

        client = groq_sdk.AsyncGroq(api_key=settings.GROQ_API_KEY)
        model = request.model or "llama-3.1-8b-instant"

        completion = await client.chat.completions.create(
            model=model,
            messages=request.messages,
        )
        text = completion.choices[0].message.content or ""
        logger.info("llm_groq_response", model=model, chars=len(text))
        return ChatResponse(response=text, provider="groq")

    except Exception as exc:
        logger.warning("llm_groq_failed", error=str(exc))
        return _echo_response(request)


def _echo_response(request: ChatRequest) -> ChatResponse:
    last_user = next(
        (
            m.get("content", "")
            for m in reversed(request.messages)
            if m.get("role") == "user"
        ),
        "",
    )
    return ChatResponse(
        response=f"[echo] {last_user}",
        provider="echo",
    )
