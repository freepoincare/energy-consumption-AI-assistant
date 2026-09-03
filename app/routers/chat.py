"""
FastAPI Router for AI Chat endpoints:
- POST /api/chat : Ask natural language questions grounded in electricity consumption data.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.ai_service import AIChatService

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Chat Message to AI Assistant",
    description="Processes user questions using OpenAI GPT with real-time dynamic context injection from the energy consumption summary."
)
async def chat_with_assistant(payload: ChatRequest):
    try:
        response = await AIChatService.process_chat(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )
