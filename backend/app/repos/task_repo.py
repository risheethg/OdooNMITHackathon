from pymongo.collection import Collection
from app.core.db_connection import get_db
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.repos.base_repo import BaseRepo

class TaskRepo(BaseRepo):
    """
    Repository for managing task documents.
    """
    def __init__(self):
        db = get_db()
        super().__init__(collection=db.get_collection("Tasks"))

    def get_by_project_id(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Finds all tasks associated with a given project ID.
        """
        return super().get_all({"project_id": project_id})


    def get_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a single task by its ID.
        """
        return super().get_by_id(task_id)


    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new task document and returns the full doc.
        """
        inserted_id = super().create(data)  # returns ObjectId
        return super().get_by_id(str(inserted_id))  # fetch doc using BaseRepo


    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a task by its ID and returns the updated document.
        """
        try:
            modified_count = super().update(task_id, update_data)
            if modified_count:
                return self.get_by_id(task_id)
            return None
        except:
            return None


    def delete_task(self, task_id: str) -> bool:
        """
        Soft deletes a task by its ID.
        """
        try:
            filter_query = {"_id": ObjectId(task_id)}
            result = self.collection.update_one(
                filter_query,
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            # log the error if needed
            return False

        
task_repo=TaskRepo()