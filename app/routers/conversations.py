"""
FastAPI Router for Conversation history endpoints:
- POST   /api/conversations       : Create a new conversation thread
- GET    /api/conversations       : List conversation history threads
- GET    /api/conversations/{id}  : Retrieve a specific conversation thread with full message history
- DELETE /api/conversations/{id}  : Delete a conversation thread
"""

from fastapi import APIRouter, HTTPException, status
from app.models.chat_models import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get(
    "",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List All Conversations",
    description="Retrieves a list of all conversation threads sorted by last updated timestamp."
)
async def list_conversations():
    return ConversationService.list_conversations()


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation Thread",
    description="Creates a new conversation thread with optional title and initial messages."
)
async def create_conversation(payload: ConversationCreate):
    return ConversationService.create_conversation(payload)


@router.get(
    "/{conv_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Conversation by ID",
    description="Retrieves complete message history for a specific conversation session."
)
async def get_conversation(conv_id: str):
    conv = ConversationService.get_conversation_by_id(conv_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{conv_id}' not found."
        )
    return conv


@router.delete(
    "/{conv_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Conversation",
    description="Deletes a conversation session by its ID."
)
async def delete_conversation(conv_id: str):
    deleted = ConversationService.delete_conversation(conv_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{conv_id}' not found."
        )
    return {"message": f"Conversation '{conv_id}' deleted successfully.", "id": conv_id}
