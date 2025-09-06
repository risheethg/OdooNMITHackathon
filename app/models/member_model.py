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