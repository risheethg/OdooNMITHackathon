from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class TaskStatus(str, Enum):
    """
    Enum for task statuses to ensure consistency.
    """
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class TaskBase(BaseModel):
    """
    Base model for task properties.
    """
    title: str
    description: Optional[str] = None
    assignee: str # User ID of the assigned team member
    due_date: datetime
    status: TaskStatus = Field(default=TaskStatus.TODO)
    is_deleted: bool = False

class TaskCreate(TaskBase):
    """
    Model for creating a new task.
    The 'created_by' field is removed as it will be set automatically by the service.
    """
    pass

class TaskUpdate(BaseModel):
    """
    Model for updating an existing task.
    All fields are optional.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
class Task(TaskBase):
    """
    Full task model with database-related fields.
    """
    task_id: str = Field(..., alias="_id")
    project_id: str
    created_by: str  # The user ID of the creator
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("task_id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v
            
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}