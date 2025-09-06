import logging
import inspect
from datetime import datetime, timezone
from typing import List, Optional

# Your project's specific imports
from app.core.logger import logs
from app.repos.chat_repo import ChatRepo
from app.repos.project_repo import project_repo
from app.models.chat_model import ChatMessage, ChatMessageCreate, ChatMessageUpdate
from app.services import llm_service # Import the new LLM service
from app.utils.websocket_manager import manager # Import for broadcasting LLM response
from app.services import notification_service # Import notification service

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

async def create_chat_message(project_id: str, user_id: str, username: str, data: ChatMessageCreate) -> ChatMessage:
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
    
    validated_message = ChatMessage.model_validate(new_message)

    # --- NOTIFICATION LOGIC ---
    # Notify all other members of the project about the new message.
    project = project_repo.get_by_id(project_id)
    if project:
        # Convert all member ObjectIds to strings
        member_id_strs = {str(m) for m in project.get("members", [])}
        
        # Get the creator's ID as a string
        creator_id = project.get("created_by")
        if creator_id:
            member_id_strs.add(str(creator_id))

        # Iterate over the clean set of string IDs
        for member_id_str in member_id_strs:
            # Don't send a notification to the user who sent the message
            if member_id_str != user_id:
                await notification_service.create_notification(
                    user_id=member_id_str,
                    message=f"New message in '{project.get('project_name')}': '{username}' said: {data.message[:30]}...'"
                )

    # --- LLM INTEGRATION ---
    # Check if the message starts with "@Gemini"
    if data.message.lower().startswith("@gemini"):
        llm_query = data.message[len("@gemini"):].strip()
        logs.define_logger(logging.INFO, None, log_name, message=f"User '{username}' triggered Gemini AI with query: '{llm_query}'")

        # Fetch recent chat history for context (e.g., last 10 messages)
        # This fetches history *including* the user's message we just saved.
        recent_history = get_chat_history(project_id, user_id, page=1, limit=10)

        # Generate response from LLM
        llm_response_text = await llm_service.generate_gemini_response(
            project_id=project_id,
            chat_history=recent_history,
            user_query=llm_query
        )

        # Store LLM's response in chat history
        llm_message_doc = {
            "project_id": project_id,
            "user_id": "gemini_ai_id", # A unique ID for the AI user
            "username": "Gemini AI",   # Display name for the AI
            "message": llm_response_text,
            "is_edited": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        llm_inserted_id = chat_repo.create(llm_message_doc)
        llm_new_message = chat_repo.get_by_id(str(llm_inserted_id))
        llm_validated_message = ChatMessage.model_validate(llm_new_message)
        logs.define_logger(logging.INFO, None, log_name, message=f"Gemini AI response stored as message '{llm_inserted_id}'.")

        # Broadcast the LLM's response immediately to all clients
        llm_broadcast_payload = {"event": "new_message", "data": llm_validated_message.model_dump(mode="json")}
        await manager.broadcast(project_id, llm_broadcast_payload)
        logs.define_logger(logging.INFO, None, log_name, message="Gemini AI response broadcasted to WebSocket clients.")

    return validated_message

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
