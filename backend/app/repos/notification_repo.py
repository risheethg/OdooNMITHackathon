from pymongo.collection import Collection
from app.core.db_connection import get_db
from typing import Optional, Dict, Any, List

from app.repos.base_repo import BaseRepo

class NotificationRepo(BaseRepo):
    """Repository for managing notification documents."""
    def __init__(self):
        db = get_db()
        super().__init__(collection=db.get_collection("notifications"))

    def get_by_user_id(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Finds all notifications for a given user, sorted by most recent."""
        query = {"user_id": user_id}
        # Sort by _id descending to get the most recent notifications
        return list(self.collection.find(query, {"is_deleted": False}).sort("_id", -1).limit(limit))

    def mark_as_read(self, notification_id: str) -> int:
        """Marks a single notification as read."""
        return self.update(notification_id, {"status": "read"})

    def mark_all_as_read_for_user(self, user_id: str) -> int:
        """Marks all unread notifications for a user as read."""
        result = self.collection.update_many(
            {"user_id": user_id, "status": "unread", "is_deleted": False},
            {"$set": {"status": "read"}}
        )
        return result.modified_count

notification_repo = NotificationRepo()