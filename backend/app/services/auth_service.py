from fastapi import Depends, HTTPException, status
# Import HTTPBearer and HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from ..repos.auth_repo import AuthRepo, auth_repo
from ..models.auth_model import User, UserCreate, TokenData
from ..core.security import verify_password, decode_access_token
import logging
import inspect
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from typing_extensions import Annotated

# Your project's specific imports
from app.core.logger import logs
from app.core import security
from app.models.auth_model import User, TokenData



# This scheme is still used by FastAPI to identify the login endpoint for the UI.
# We don't use it directly for getting the token anymore, but it's good to keep.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- NEW: Use HTTPBearer for Authorization ---
# This scheme tells Swagger UI to use the simple "Authorization: Bearer <token>" flow.
bearer_scheme = HTTPBearer()

class AuthService:
    """
    Service layer containing all business logic for authentication.
    """
    def __init__(self, repo: AuthRepo = Depends(AuthRepo)):
        self.repo = repo

    def register_user(self, user_data: UserCreate) -> dict:
        """
        Handles user registration logic and returns the created user as a dict.
        """
        if self.repo.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already registered."
            )
        if self.repo.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered."
            )
        
        return self.repo.create_user(user_data)

    def authenticate_user(self, username: str, password: str) -> dict | None:
        """
        Authenticates a user and returns their data as a dict if successful.
        """
        user_dict = self.repo.get_user_by_username(username)
        if not user_dict:
            return None
        
        hashed_password = user_dict.get("password")
        if not hashed_password or not verify_password(password, hashed_password):
            return None
            
        return user_dict


def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Decodes a JWT token string, validates it, and retrieves the corresponding user.
    This is a direct function used by WebSockets.
    
    :param token: The raw JWT token string.
    :return: The authenticated User object or None if authentication fails.
    """
    log_name = inspect.stack()[0]
    try:
        payload = security.decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        logs.define_logger(logging.WARNING, None, log_name, message="WebSocket auth failed: Could not validate token.")
        return None

    user_dict = auth_repo.get_user_by_username(username=token_data.username)
    if user_dict is None:
        logs.define_logger(logging.WARNING, None, log_name, message=f"WebSocket auth failed: User '{username}' not found.")
        return None
        
    # Use model_validate to correctly handle field aliasing (e.g., _id -> user_id)
    # and type conversion (ObjectId -> str).
    return User.model_validate(user_dict)
# --- UPDATED: Dependency function to use the new scheme ---
def get_current_active_user(
    # Use the new bearer_scheme. It returns a credentials object.
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    repo: AuthRepo = Depends(AuthRepo)
) -> User:
    """
    Dependency to get the current authenticated user from a token.
    Validates the token and returns the user as a Pydantic model.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # The actual token string is in the `credentials` attribute of the object.
    token = credentials.credentials
    
    token_data = decode_access_token(token)
    if not token_data or not token_data.get("username"):
        raise credentials_exception
        
    user_dict = repo.get_user_by_username(token_data["username"])
    if user_dict is None:
        raise credentials_exception
    
    # Convert _id to str for the Pydantic model
    if "_id" in user_dict:
        user_dict["_id"] = str(user_dict["_id"])
        
    return User.model_validate(user_dict)
