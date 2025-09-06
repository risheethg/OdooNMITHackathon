from typing import List, Dict, Any
from pymongo import ASCENDING

from .base_repo import BaseRepo
from ..core.db_connection import get_db

CHAT_COLLECTION_NAME = "chat_history"

class ChatRepo(BaseRepo):
    """Repository for chat message database operations."""

    def __init__(self):
        db = get_db()
        chat_collection = db.get_collection(CHAT_COLLECTION_NAME)
        super().__init__(collection=chat_collection)

    def get_history_for_project_paginated(
        self, project_id: str, page: int = 1, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetches chat history for a project with pagination, sorted by creation time.
        """
        skip_count = (page - 1) * limit
        query = {"project_id": project_id, "is_deleted": False}
        
        # Fetch documents, sort by timestamp, skip for pagination, and limit results
        cursor = self.collection.find(query).sort("created_at", ASCENDING).skip(skip_count).limit(limit)
        return list(cursor)
