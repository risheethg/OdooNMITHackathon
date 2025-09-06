from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from typing import List, Optional, Any
from datetime import datetime

# --- Core Model ---
class Project(BaseModel):
    project_id: str = Field(..., alias="_id")
    project_name: str
    description: Optional[str] = None
    jira_project_key: Optional[str] = None
    created_by: str
    members: List[str] = Field(default_factory=list) # <-- ADDED THIS FIELD
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("project_id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v
            
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# --- API Input Models ---
class ProjectCreate(BaseModel):
    project_name: str = Field(..., description="Name for the new project.")
    description: Optional[str] = Field(None, description="Description for the new project.")

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, description="Optional new name for the project.")
    description: Optional[str] = Field(None, description="Optional new description for the project.")

class ProjectMemberUpdate(BaseModel):
    user_id: str = Field(..., description="The ID of the user to add or remove from the project.")

