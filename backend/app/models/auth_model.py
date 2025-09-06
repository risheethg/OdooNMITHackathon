from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any
from bson import ObjectId

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    """
    User model for responses. Does not include the password.
    """
    user_id: str = Field(..., alias="_id")

    @field_validator("user_id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        """Convert ObjectId to string before validation."""
        if isinstance(v, ObjectId):
            return str(v)
        # If it's already a string (or something else), let it pass through.
        return v

    class Config: # Pydantic V2 uses model_config, but Config still works for backward compatibility
        # Allow population by field name (e.g., '_id') in addition to alias ('user_id')
        populate_by_name = True
        # Allow Pydantic to handle types like ObjectId from the database.
        arbitrary_types_allowed = True
        # Define a custom JSON encoder for ObjectId to ensure it's always converted to a string.
        json_encoders = {
            ObjectId: str
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
