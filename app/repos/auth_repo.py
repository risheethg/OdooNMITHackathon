from pymongo.collection import Collection
from pymongo.database import Database
from typing import Dict, Any, Optional
from fastapi import Depends

# Your project's specific imports
from .base_repo import BaseRepo
from ..models.auth_model import UserCreate
from ..core.security import get_password_hash
from ..core.db_connection import get_db # <-- Import YOUR get_db function

USER_COLLECTION_NAME = "users"

class AuthRepo(BaseRepo):
    """
    Repository for authentication-related database operations.
    This version initializes its own database connection by calling the
    get_db dependency function internally.
    """

    def __init__(self):
        """
        Initializes the repository. It directly calls the `get_db` dependency
        to get the database instance and then gets the 'users' collection.
        """
        db = get_db()
        user_collection = db.get_collection(USER_COLLECTION_NAME)
        super().__init__(collection=user_collection)

    def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Creates a new user document, hashing the password before insertion.
        """
        user_dict = user_data.model_dump()
        user_dict["password"] = get_password_hash(user_data.password)
        return self.create(user_dict)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a user by their username.
        """
        return self.find_one_by({"username": username})

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a user by their email address.
        """
        return self.find_one_by({"email": email})

