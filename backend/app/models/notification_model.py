from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class NotificationStatus(str, Enum):
    """Enum for notification statuses."""
    UNREAD = "unread"
    READ = "read"

class NotificationBase(BaseModel):
    """Base model for notification properties."""
    user_id: str  # The ID of the user who receives the notification
    message: str
    link: Optional[str] = None  # A URL to the relevant item (e.g., /tasks/{task_id})
    status: NotificationStatus = Field(default=NotificationStatus.UNREAD)

class Notification(NotificationBase):
    """Full notification model with database-related fields."""
    notification_id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("notification_id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class NotificationUpdate(BaseModel):
    """Model for updating a notification's status."""
    status: NotificationStatus