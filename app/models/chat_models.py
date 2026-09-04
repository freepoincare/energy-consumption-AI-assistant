"""
Pydantic schemas for AI chat and conversation persistence.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


class MessageItem(BaseModel):
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'", example="user")
    content: str = Field(..., description="Message text content", example="What was my highest electricity usage day?")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp when message was created")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query", example="How much electricity did I use on average?")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation session ID")


class ChatResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation session ID")
    reply: str = Field(..., description="AI assistant response")
    used_summary: bool = Field(default=True, description="Whether summary context was injected")
    tool_calls_made: List[Dict[str, Any]] = Field(default_factory=list, description="List of Function Calling tool invocations made during this request")
    created_at: str = Field(..., description="Timestamp of the response")


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default=None, description="Conversation title / topic summary", example="August Electricity Q&A")
    messages: Optional[List[MessageItem]] = Field(default_factory=list, description="List of messages")


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Updated conversation title")
    messages: Optional[List[MessageItem]] = Field(default=None, description="Updated list of messages")


class ConversationResponse(BaseModel):
    id: str = Field(..., description="Unique conversation ID")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="ISO timestamp when created")
    updated_at: str = Field(..., description="ISO timestamp when last updated")
    messages: List[MessageItem] = Field(default_factory=list, description="Complete message history")


class ConversationListResponse(BaseModel):
    total_count: int = Field(..., description="Total number of conversations")
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")
