from typing import Dict, Any, Optional

# Your project's specific imports
from .base_repo import BaseRepo
from ..models.auth_model import UserCreate
from ..core.security import get_password_hash
from ..core.db_connection import get_db

USER_COLLECTION_NAME = "users"

class AuthRepo(BaseRepo):
    """
    Repository for authentication-related database operations.
    This version is updated to work with the new soft-delete BaseRepo.
    """

    def __init__(self):
        """
        Initializes the repository by getting the database connection and
        the specific collection for users.
        """
        db = get_db()
        user_collection = db.get_collection(USER_COLLECTION_NAME)
        super().__init__(collection=user_collection)

    def create_user(self, user_data: UserCreate) -> Optional[Dict[str, Any]]:
        """
        Creates a new user document, hashing the password before insertion.
        It uses the new BaseRepo which returns an ObjectId, and then fetches
        the created document.
        """
        user_dict = user_data.model_dump()
        user_dict["password"] = get_password_hash(user_data.password)
        
        # self.create() from the new BaseRepo returns an ObjectId
        inserted_id = self.create(user_dict)
        
        # Fetch the document by its new ID to return the full object
        return self.get_by_id(str(inserted_id))

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a non-deleted user by their username using the new `get_one` method.
        """
        return self.get_one({"username": username})

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a non-deleted user by their email address using the new `get_one` method.
        """
        return self.get_one({"email": email})

auth_repo = AuthRepo()