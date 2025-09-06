from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class TeamMember(BaseModel):
    """
    Schema for a team member.
    """
    user_id: str
    email: EmailStr
    role: str = "member"

class MemberAdditionRequest(BaseModel):
    """
    Schema for adding a new team member.
    """
    user_id: str
    email: EmailStr
    role: Optional[str] = "member"

class MemberRemovalRequest(BaseModel):
    """
    Schema for removing a team member.
    """
    user_id: str

class MemberUpdate(BaseModel):
    """Schema for adding or removing a member from a project."""
    user_id: str = Field(..., description="The ID of the user to add or remove.")