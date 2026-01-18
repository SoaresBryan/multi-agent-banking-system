import logging
from datetime import datetime
from typing import Optional

from pymongo import MongoClient

from app.config import settings

logger = logging.getLogger(__name__)


class ChatMemory:
    """Gerencia o historico de conversas no MongoDB."""

    def __init__(self, agent_id: str, conversation_id: str):
        self.agent_id = agent_id
        self.conversation_id = conversation_id
        self.session_id = f"{agent_id}:{conversation_id}"
        self._client: Optional[MongoClient] = None
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._client = MongoClient(settings.mongo_uri)
            db = self._client[settings.mongo_db]
            self._collection = db["conversations"]
        return self._collection

    def _doc(self, msg_type: str, content: str) -> dict:
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "message": {"type": msg_type, "content": content},
            "created_at": datetime.utcnow(),
        }

    def add_user_message(self, message: str) -> None:
        try:
            self.collection.insert_one(self._doc("human", message))
            logger.debug(f"[chat_memory] User message saved: {message[:50]}...")
        except Exception as e:
            logger.error(f"[chat_memory] Error saving user message: {e}")

    def add_ai_message(self, message: str) -> None:
        try:
            self.collection.insert_one(self._doc("ai", message))
            logger.debug(f"[chat_memory] AI message saved: {message[:50]}...")
        except Exception as e:
            logger.error(f"[chat_memory] Error saving AI message: {e}")

    def get_messages(self) -> list[dict]:
        try:
            docs = self.collection.find({"session_id": self.session_id}).sort(
                "created_at", 1
            )
            messages = []
            for d in docs:
                messages.append({
                    "role": "user" if d["message"]["type"] == "human" else "assistant",
                    "content": d["message"]["content"],
                })
            logger.debug(f"[chat_memory] Retrieved {len(messages)} messages")
            return messages
        except Exception as e:
            logger.error(f"[chat_memory] Error retrieving messages: {e}")
            return []

    def clear(self) -> None:
        try:
            self.collection.delete_many({"session_id": self.session_id})
            logger.debug(f"[chat_memory] Cleared messages for session {self.session_id}")
        except Exception as e:
            logger.error(f"[chat_memory] Error clearing messages: {e}")

    def close(self) -> None:
        if self._client:
            self._client.close()


def get_memory(agent_id: str, conversation_id: str) -> ChatMemory:
    return ChatMemory(agent_id, conversation_id)


async def create_indexes(collection) -> None:
    logger.debug("[chat_memory] Creating indexes for 'conversations' collection")

    try:
        await collection.create_index("session_id")
        await collection.create_index([("agent_id", 1), ("conversation_id", 1)])
        await collection.create_index("created_at")
        logger.debug("[chat_memory] Indexes created successfully")
    except Exception as e:
        logger.error(f"[chat_memory] Error creating indexes: {e}")
