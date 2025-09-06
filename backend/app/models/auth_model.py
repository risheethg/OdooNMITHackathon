from pydantic import BaseModel, EmailStr, Field
from typing import Optional

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

    class Config:
        # Allows Pydantic to populate the 'id' field from the '_id' key
        populate_by_name = True
        # Pydantic v2's equivalent of orm_mode
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
