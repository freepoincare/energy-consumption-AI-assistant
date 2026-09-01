"""
Pydantic schemas for AI chat requests and responses (Placeholders for Step 5).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'", example="user")
    content: str = Field(..., description="Message text content", example="What was my highest electricity usage day?")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query", example="How much electricity did I use on average?")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation session ID")


class ChatResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation session ID")
    reply: str = Field(..., description="AI assistant response")
    used_summary: bool = Field(default=True, description="Whether summary context was injected")
    created_at: str = Field(..., description="Timestamp of the response")
