import logging
import inspect
from datetime import datetime, timezone
from typing import List, Optional

# Your project's specific imports
from app.core.logger import logs
from app.repos.chat_repo import ChatRepo
from app.repos.project_repo import project_repo
from app.models.chat_model import ChatMessage, ChatMessageCreate, ChatMessageUpdate

# A single instance for the service layer
chat_repo = ChatRepo()
# Replace the function in services/chat_service.py with this one:


def _is_user_project_member(project_id: str, user_id: str) -> bool:
    """
    Checks if a user is a member or the creator of a project.
    Handles comparison between string user_id and database ObjectId types.
    """
    project = project_repo.get_by_id(project_id)
    
    if not project:
        return False

    # Check creator: Convert the ObjectId from the DB to a string for comparison.
    creator_obj = project.get("created_by")
    if creator_obj and str(creator_obj) == user_id:
        return True

    # Check members: Convert each ObjectId in the list to a string for comparison.
    members_list = project.get("members", [])
    return any(str(member_id) == user_id for member_id in members_list)



def get_chat_history(project_id: str, user_id: str, page: int, limit: int) -> List[ChatMessage]:
    """Fetches paginated chat history for a project after verifying user membership."""
    log_name = inspect.stack()[0]
    logs.define_logger(logging.INFO, None, log_name, message=f"Attempting to fetch chat history for project '{project_id}' for user '{user_id}'.")
    
    if not _is_user_project_member(project_id, user_id):
        logs.define_logger(logging.WARNING, None, log_name, message=f"Permission denied: User '{user_id}' is not a member of project '{project_id}'.")
        raise PermissionError("User is not a member of this project.")
    
    history_docs = chat_repo.get_history_for_project_paginated(project_id, page, limit)
    logs.define_logger(logging.INFO, None, log_name, message=f"Successfully retrieved {len(history_docs)} messages for project '{project_id}'.")
    return [ChatMessage.model_validate(doc) for doc in history_docs]

def create_chat_message(project_id: str, user_id: str, username: str, data: ChatMessageCreate) -> ChatMessage:
    """Creates a new chat message after verifying user membership."""
    log_name = inspect.stack()[0]
    logs.define_logger(logging.INFO, None, log_name, message=f"User '{username}' attempting to send message to project '{project_id}'.")

    if not _is_user_project_member(project_id, user_id):
        logs.define_logger(logging.WARNING, None, log_name, message=f"Permission denied: User '{user_id}' is not a member of project '{project_id}'.")
        raise PermissionError("User is not a member of this project.")
    
    now = datetime.now(timezone.utc)
    message_doc = {
        "project_id": project_id,
        "user_id": user_id,
        "username": username,
        "message": data.message,
        "is_edited": False,
        "created_at": now,
        "updated_at": now,
    }
    inserted_id = chat_repo.create(message_doc)
    new_message = chat_repo.get_by_id(str(inserted_id))
    logs.define_logger(logging.INFO, None, log_name, message=f"Successfully created message '{inserted_id}' in project '{project_id}'.")
    return ChatMessage.model_validate(new_message)

def edit_chat_message(message_id: str, user_id: str, data: ChatMessageUpdate) -> Optional[ChatMessage]:
    """Updates an existing chat message after verifying ownership."""
    log_name = inspect.stack()[0]
    logs.define_logger(logging.INFO, None, log_name, message=f"User '{user_id}' attempting to edit message '{message_id}'.")

    original_message = chat_repo.get_by_id(message_id)
    if not original_message:
        logs.define_logger(logging.WARNING, None, log_name, message=f"Edit failed: Message with ID '{message_id}' not found.")
        raise ValueError("Message not found.")
    
    # Ensure a robust string-to-string comparison for ownership
    if str(original_message.get("user_id")) != user_id:
        logs.define_logger(logging.WARNING, None, log_name, message=f"Permission denied: User '{user_id}' is not the author of message '{message_id}'.")
        raise PermissionError("User is not the author of this message.")

    update_data = {
        "message": data.message,
        "is_edited": True,
        "updated_at": datetime.now(timezone.utc)
    }
    modified_count = chat_repo.update(message_id, update_data)

    if modified_count > 0:
        updated_message = chat_repo.get_by_id(message_id)
        logs.define_logger(logging.INFO, None, log_name, message=f"Successfully updated message '{message_id}'.")
        return ChatMessage.model_validate(updated_message)
        
    logs.define_logger(logging.INFO, None, log_name, message=f"No changes made to message '{message_id}'. Update data was likely the same.")
    return None

