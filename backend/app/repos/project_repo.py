from pymongo.collection import Collection
from pymongo.results import UpdateResult
from typing import Dict, Any, Optional
from bson import ObjectId

from app.repos.base_repo import BaseRepo

# Assuming project_repo is an instance of ProjectRepo and configured correctly.
# project_repo = ProjectRepo(collection=db.projects)

class ProjectRepo(BaseRepo):
    """
    Repository for managing project documents.
    """
    def __init__(self, collection: Collection):
        super().__init__(collection)

    def add_member(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Adds a member to a project's members list using $addToSet to avoid duplicates."""
        # Convert string ID to ObjectId if needed
        object_id = ObjectId(project_id)
        
        filter_query = {"_id": object_id}
        update_data = {"$addToSet": {"members": user_id}}
        
        # Use update_one for atomic update and get the result
        result: UpdateResult = self._collection.update_one(filter_query, update_data)
        
        if result.modified_count > 0:
            return self.find_one_by(filter_query)
        return None

    def remove_member(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Removes a member from a project's members list using $pull."""
        # Convert string ID to ObjectId if needed
        object_id = ObjectId(project_id)

        filter_query = {"_id": object_id}
        update_data = {"$pull": {"members": user_id}}
        
        result: UpdateResult = self._collection.update_one(filter_query, update_data)

        if result.modified_count > 0:
            return self.find_one_by(filter_query)
        return None

