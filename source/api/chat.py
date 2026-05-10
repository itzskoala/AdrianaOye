from fastapi import APIRouter
from pydantic import BaseModel

from source.agent import adriana

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Single endpoint the frontend calls. Routes to Adriana agent."""
    reply = await adriana.chat(req.message)
    return ChatResponse(reply=reply)
