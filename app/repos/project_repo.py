from .base_repo import BaseRepo
from pymongo.collection import Collection
from typing import Dict, Any, List

class ProjectRepo(BaseRepo):
    """
    Repository for managing project documents.
    """
    def __init__(self, collection: Collection):
        super().__init__(collection)

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