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
        Uses the get_all method from BaseRepo.
        """
        return self.get_all({"project_id": project_id})

    def get_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a single task by its ID using the inherited method.
        """
        return super().get_by_id(task_id)

    def create_task(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Creates a new task document and returns the created document.
        """
        inserted_id = self.create(data)
        if inserted_id:
            return self.get_by_id(str(inserted_id))
        return None

    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a task by its ID.
        """
        modified_count = self.update(task_id, update_data)
        if modified_count > 0:
            return self.get_by_id(task_id)
        return None

    def delete_task(self, task_id: str) -> bool:
        """
        Soft deletes a task by its ID.
        """
        modified_count = self.delete_soft(task_id)
        return modified_count > 0
        
task_repo=TaskRepo()