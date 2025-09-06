import logging
import inspect
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from starlette.responses import JSONResponse
from starlette import status

# Your project's specific imports
from app.core.logger import logs
from app.services import chat_service, auth_service
from app.models.auth_model import User
from app.models.chat_model import ChatMessage, ChatMessageCreate, ChatMessageUpdate
from app.utils.responses import response
from app.utils.websocket_manager import manager # Keep for broadcasting

router = APIRouter(prefix="/projects/{project_id}/chat", tags=["Chat"])

# --- NEW ENDPOINT ADDED HERE ---
@router.post("/")
async def send_new_chat_message(
    project_id: str,
    message_data: ChatMessageCreate,
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    Send a new chat message to a project.
    This is a standard RESTful endpoint for sending messages.
    """
    log_name = inspect.stack()[0]
    try:
        logs.define_logger(logging.INFO, None, log_name, message=f"User '{current_user.username}' attempting to POST message to project '{project_id}'.")
        
        # Call the existing service function to create the message
        new_message = await chat_service.create_chat_message(
            project_id=project_id,
            user_id=current_user.user_id,
            username=current_user.username,
            data=message_data
        )

        # Broadcast the new message to any connected WebSocket clients
        broadcast_payload = {"event": "new_message", "data": new_message.model_dump(mode="json")}
        await manager.broadcast(project_id, broadcast_payload)
        logs.define_logger(logging.INFO, None, log_name, message="Message broadcasted to WebSocket clients.")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.success(data=new_message.model_dump(mode="json"), message="Message sent successfully.")
        )
    except PermissionError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=response.failure(message=str(e))
        )
    except Exception as e:
        logs.define_logger(logging.CRITICAL, None, log_name, message=f"An unexpected error occurred while sending a message to project '{project_id}': {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.failure(message="An unexpected error occurred.")
        )


@router.get("/")
async def get_project_chat_history(
    project_id: str,
    current_user: User = Depends(auth_service.get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Messages per page")
):
    """
    Retrieve the chat history for a specific project.
    """
    # ... existing code for getting history ...
    log_name = inspect.stack()[0]
    try:
        history = chat_service.get_chat_history(project_id, current_user.user_id, page, limit)
        history_data = [msg.model_dump(mode="json") for msg in history]
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.success(data=history_data, message="Chat history retrieved successfully.")
        )
    except PermissionError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=response.failure(message=str(e))
        )
    except Exception as e:
        logs.define_logger(logging.CRITICAL, None, log_name, message=f"An unexpected error occurred while fetching chat history for project '{project_id}': {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.failure(message="An unexpected error occurred.")
        )


@router.put("/{message_id}")
async def edit_existing_chat_message(
    project_id: str,
    message_id: str,
    update_data: ChatMessageUpdate,
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    Edit an existing chat message.
    """
    # ... existing code for editing a message ...
    log_name = inspect.stack()[0]
    try:
        updated_message = chat_service.edit_chat_message(message_id, current_user.user_id, update_data)
        if not updated_message:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=response.failure(message="Message not found or no changes made.")
            )

        # Broadcast the edit event to WebSocket clients
        broadcast_payload = {"event": "edit_message", "data": updated_message.model_dump(mode="json")}
        await manager.broadcast(project_id, broadcast_payload)
        logs.define_logger(logging.INFO, None, log_name, message="Edit event broadcasted to WebSocket clients.")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.success(data=updated_message.model_dump(mode="json"), message="Message updated successfully.")
        )
    except PermissionError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=response.failure(message=str(e))
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.failure(message=str(e))
        )
    except Exception as e:
        logs.define_logger(logging.CRITICAL, None, log_name, message=f"An unexpected error occurred while editing message '{message_id}': {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.failure(message="An unexpected error occurred.")
        )
