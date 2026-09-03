"""
Conversation Service and Firestore Repository.

Encapsulates all persistence and CRUD logic for the `conversations` collection in Firestore.
Includes in-memory fallback for local environments without cloud credentials.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.models.chat_models import (
    MessageItem,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse
)
from app.database.firestore import get_firestore_db

logger = logging.getLogger("app.services.conversation_service")


class FirestoreConversationRepository:
    """
    Repository for managing conversation threads in Firestore 'conversations' collection.
    """
    COLLECTION_NAME = "conversations"

    def __init__(self):
        self._mock_store: Dict[str, Dict[str, Any]] = {}

    def get_all(self) -> List[Dict[str, Any]]:
        db = get_firestore_db()
        if db is not None:
            try:
                docs = db.collection(self.COLLECTION_NAME).stream()
                conversations = []
                for doc in docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    conversations.append(d)
                if conversations:
                    return sorted(conversations, key=lambda x: x.get("updated_at", ""), reverse=True)
            except Exception as e:
                logger.warning(f"Error fetching conversations from Firestore: {e}")

        # Fallback in-memory
        return sorted(list(self._mock_store.values()), key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_by_id(self, conv_id: str) -> Optional[Dict[str, Any]]:
        db = get_firestore_db()
        if db is not None:
            try:
                doc_ref = db.collection(self.COLLECTION_NAME).document(conv_id)
                doc = doc_ref.get()
                if doc.exists:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    return d
                return None
            except Exception as e:
                logger.warning(f"Error getting conversation {conv_id} from Firestore: {e}")

        return self._mock_store.get(conv_id)

    def create(self, data: ConversationCreate, conv_id: Optional[str] = None) -> Dict[str, Any]:
        cid = conv_id or str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()
        title = data.title or "New Conversation"
        messages_dict = [m.model_dump() if hasattr(m, "model_dump") else m for m in data.messages]

        doc_data = {
            "id": cid,
            "title": title,
            "created_at": now_str,
            "updated_at": now_str,
            "messages": messages_dict
        }

        db = get_firestore_db()
        if db is not None:
            try:
                db.collection(self.COLLECTION_NAME).document(cid).set(doc_data)
            except Exception as e:
                logger.warning(f"Error creating conversation {cid} in Firestore: {e}")

        self._mock_store[cid] = doc_data
        return doc_data

    def append_message_exchange(
        self,
        conv_id: str,
        user_message: str,
        assistant_reply: str,
        default_title_prefix: str = "Chat"
    ) -> Dict[str, Any]:
        """
        Appends user message and assistant reply to an existing or new conversation.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        user_msg = {"role": "user", "content": user_message, "timestamp": now_str}
        assistant_msg = {"role": "assistant", "content": assistant_reply, "timestamp": now_str}

        existing = self.get_by_id(conv_id)
        if not existing:
            # Generate title from user query snippet
            title_snippet = user_message[:30] + ("..." if len(user_message) > 30 else "")
            doc_data = {
                "id": conv_id,
                "title": f"{default_title_prefix}: {title_snippet}",
                "created_at": now_str,
                "updated_at": now_str,
                "messages": [user_msg, assistant_msg]
            }
        else:
            doc_data = existing
            messages = doc_data.get("messages", [])
            messages.append(user_msg)
            messages.append(assistant_msg)
            doc_data["messages"] = messages
            doc_data["updated_at"] = now_str

        db = get_firestore_db()
        if db is not None:
            try:
                db.collection(self.COLLECTION_NAME).document(conv_id).set(doc_data)
            except Exception as e:
                logger.warning(f"Error persisting conversation {conv_id} to Firestore: {e}")

        self._mock_store[conv_id] = doc_data
        return doc_data

    def delete(self, conv_id: str) -> bool:
        found = False
        db = get_firestore_db()
        if db is not None:
            try:
                doc_ref = db.collection(self.COLLECTION_NAME).document(conv_id)
                if doc_ref.get().exists:
                    doc_ref.delete()
                    found = True
            except Exception as e:
                logger.warning(f"Error deleting conversation {conv_id} from Firestore: {e}")

        if conv_id in self._mock_store:
            del self._mock_store[conv_id]
            found = True

        return found


# Singleton repository instance
conversation_repository = FirestoreConversationRepository()


class ConversationService:
    @staticmethod
    def list_conversations() -> ConversationListResponse:
        records = conversation_repository.get_all()
        return ConversationListResponse(
            total_count=len(records),
            conversations=[ConversationResponse(**r) for r in records]
        )

    @staticmethod
    def get_conversation_by_id(conv_id: str) -> Optional[ConversationResponse]:
        record = conversation_repository.get_by_id(conv_id)
        if record:
            return ConversationResponse(**record)
        return None

    @staticmethod
    def create_conversation(data: ConversationCreate) -> ConversationResponse:
        created = conversation_repository.create(data)
        return ConversationResponse(**created)

    @staticmethod
    def delete_conversation(conv_id: str) -> bool:
        return conversation_repository.delete(conv_id)

    @staticmethod
    def record_chat_exchange(conv_id: str, user_msg: str, assistant_reply: str) -> Dict[str, Any]:
        return conversation_repository.append_message_exchange(conv_id, user_msg, assistant_reply)
