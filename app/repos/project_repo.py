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

# Create a single instance that can be imported by services
project_repo = ProjectRepo()