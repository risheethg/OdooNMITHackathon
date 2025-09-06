from typing import Dict, Any, Optional

# Import the base class and the core DB connection
from .base_repo import BaseRepo
from ..core.db_connection import get_db

class ProjectRepo(BaseRepo):
    """
    Repository for managing project documents in the 'Projects' collection.
    """
    def __init__(self):
        db = get_db()
        super().__init__(collection=db.get_collection("Projects"))

    def get_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Custom method to find a single non-deleted project by its name.
        """
        return self.get_one({"project_name": project_name})
    def add_team_member(self, project_id: str, member: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Adds a new member to a project's team_members list.
        """
        filter_query = {"project_id": project_id}
        update_data = {"$addToSet": {"team_members": member}}
        self._collection.update_one(filter_query, update_data)
        return self.find_one_by(filter_query)

    def remove_team_member(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Removes a member from a project's team_members list.
        """
        filter_query = {"project_id": project_id}
        update_data = {"$pull": {"team_members": {"user_id": user_id}}}
        self._collection.update_one(filter_query, update_data)
        return self.find_one_by(filter_query)

# Create a single instance that can be imported by services
project_repo = ProjectRepo()