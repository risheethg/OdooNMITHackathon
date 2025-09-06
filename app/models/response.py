from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar

# A generic TypeVar to allow the data field to hold any Pydantic model
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """
    A generic response model for standardizing API responses.
    """
    status: str = Field(..., description="The status of the response ('success' or 'error').")
    message: Optional[str] = Field(None, description="A message providing details about the response.")
    status_code: int = Field(..., description="The HTTP status code.")
    data: Optional[T] = Field(None, description="The data payload of the response.")
