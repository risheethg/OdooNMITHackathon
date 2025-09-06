from pymongo.collection import Collection
from pymongo.results import UpdateResult
from typing import Dict, Any, Optional
from bson import ObjectId

from app.repos.base_repo import BaseRepo
from app.core.db_connection import get_db

# Assuming project_repo is an instance of ProjectRepo and configured correctly.
# project_repo = ProjectRepo(collection=db.projects)

class ProjectRepo(BaseRepo):
    """
    Repository for managing project documents.
    """
    def __init__(self):
        db = get_db()
        super().__init__(collection=db.get_collection("Projects"))

    def get_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Custom method to find a single non-deleted project by its name.
        """
        return self.get_one({"project_name": project_name})

    def _add_mem_to_proj(self, item_id: str, update_data: Dict[str, Any]) -> int:
        """
        CORRECT IMPLEMENTATION using update_one.
        This method correctly applies update operators to a document.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(item_id)},
            update_data  # `update_one` correctly interprets {"$addToSet": ...}
        )
        return result.modified_count

    def add_member(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Adds a member to a project's members list using $addToSet to avoid duplicates."""
        # Use the update method from BaseRepo, which handles ObjectId conversion.
        update_data = {"$addToSet": {"members": user_id}}
        modified_count = self._add_mem_to_proj(project_id, update_data)

        if modified_count > 0:
            # If successful, fetch the updated document using the reliable get_by_id.
            return self.get_by_id(project_id)
        return None
    
    def _remove_mem_from_proj(self, item_id: str, update_data: Dict[str, Any]) -> int:
        """
        Private helper to remove a member using update_one with a $pull operator.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(item_id)},
            update_data  # `update_one` correctly interprets {"$pull": ...}
        )
        return result.modified_count

    def remove_member(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Removes a member from a project's members list using $pull."""
        update_data = {"$pull": {"members": user_id}}
        modified_count = self._remove_mem_from_proj(project_id, update_data)

        if modified_count > 0:
            # If successful, fetch the updated document.
            return self.get_by_id(project_id)
        return None

project_repo=ProjectRepo()
