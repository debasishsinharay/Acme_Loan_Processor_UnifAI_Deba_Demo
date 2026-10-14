"""Acme Loan Processor backend."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# UnifAI demo toggle: install it before the agents (and any unifai_guard) are imported.
import unifai_toggle

unifai_toggle.install()

import logging

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from agents.orchestrator import handle_chat

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("acme")

app = FastAPI(title="Acme Loan Processor")


@app.middleware("http")
async def unifai_toggle_middleware(request: Request, call_next):
    """Applies the UnifAI toggle from the frontend to this request."""
    unifai_toggle.set_enabled(unifai_toggle.enabled_from_header(request.headers.get(unifai_toggle.HEADER)))
    response = await call_next(request)
    response.headers[unifai_toggle.HEADER] = "on" if unifai_toggle.is_enabled() else "off"
    return response


class Attachment(BaseModel):
    name: str
    type: str = ""
    content: str = ""


class ChatRequest(BaseModel):
    message: str
    attachments: list[Attachment] = []


class ChatResponse(BaseModel):
    response: str
    agent: str
    unifai: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await handle_chat(request.message, [a.model_dump() for a in request.attachments])
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("chat request failed")
        raise HTTPException(status_code=500, detail=f"The request failed: {exc}") from exc
    return ChatResponse(
        response=result["response"],
        agent=result["agent"],
        unifai="on" if unifai_toggle.is_enabled() else "off",
    )
