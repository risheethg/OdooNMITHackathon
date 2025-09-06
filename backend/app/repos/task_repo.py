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
        return self.find_by({"project_id": project_id, "is_deleted": False})

    def get_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a single task by its ID.
        """
        try:
            return self.find_one_by({"_id": ObjectId(task_id), "is_deleted": False})
        except:
            return None

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new task document.
        """
        return self.create(data)

    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a task by its ID.
        """
        try:
            filter_query = {"_id": ObjectId(task_id)}
            return self.update_one(filter_query, {"$set": update_data})
        except:
            return None

    def delete_task(self, task_id: str) -> bool:
        """
        Soft deletes a task by its ID.
        """
        try:
            filter_query = {"_id": ObjectId(task_id)}
            result = self._collection.update_one(filter_query, {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}})
            return result.modified_count > 0
        except:
            return False
        
task_repo=TaskRepo()