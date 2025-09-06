from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Any
from datetime import datetime, timezone
from bson import ObjectId

class ChatMessage(BaseModel):
    id: str = Field(..., alias="_id")
    project_id: str
    user_id: str
    username: str
    message: str
    is_edited: bool = False
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        """Convert ObjectId to string before validation for the 'id' field."""
        if isinstance(v, ObjectId):
            return str(v)
        # If it's already a string, let it pass through.
        return v

    # Pydantic V2 model configuration
    model_config = ConfigDict(
        populate_by_name=True,        # Allows using the 'id' field name to be populated by the '_id' alias from data.
        arbitrary_types_allowed=True  # Important for robust handling of external types like ObjectId.
    )

# --- API Input Models (Unchanged) ---
class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, description="The content of the chat message.")

class ChatMessageUpdate(BaseModel):
    message: str = Field(..., min_length=1, description="The updated content of the chat message.")

class GeminiRequest(BaseModel):
    prompt: str = Field(..., description="The user's prompt for the Gemini model.")
