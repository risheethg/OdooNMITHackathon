import logging
import inspect
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from starlette import status

from app.utils.websocket_manager import manager
from app.core.logger import logs
from app.services import auth_service, chat_service
from app.models.chat_model import ChatMessageCreate

router = APIRouter(tags=["Websockets"])

@router.websocket("/ws/chat/{project_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...)
):
    """Handles real-time chat connections."""
    log_name = inspect.stack()[0]
    
    # 1. Authenticate the user from the token
    try:
        current_user = auth_service.get_current_user_from_token(token)
        if not current_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token or user not found.")
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed.")
        return

    # 2. Authorize: Check if the user is a member of the project
    if not chat_service._is_user_project_member(project_id, current_user.user_id):
        logs.define_logger(logging.WARNING, None, log_name, message=f"WebSocket connection denied for user '{current_user.username}' to project '{project_id}'. Not a member.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Forbidden: Not a project member.")
        return

    # 3. If authorized, accept the connection and add to the broadcast list
    await websocket.accept()
    await manager.connect(project_id, websocket)
    logs.define_logger(logging.INFO, None, log_name, message=f"WebSocket accepted for user '{current_user.username}' on project '{project_id}'.")
    
    try:
        while True:
            # 4. Listen for incoming messages
            message_text = await websocket.receive_text()
            
            # 5. Save the message to the database
            message_data = ChatMessageCreate(message=message_text)
            new_message = chat_service.create_chat_message(
                project_id=project_id,
                user_id=current_user.user_id,
                username=current_user.username,
                data=message_data
            )
            
            # 6. Broadcast the new message to all clients in the project room
            broadcast_payload = {"event": "new_message", "data": new_message.model_dump(mode="json")}
            await manager.broadcast(project_id, broadcast_payload)
            logs.define_logger(logging.INFO, None, log_name, message=f"User '{current_user.username}' sent message to project '{project_id}'. Broadcasted.")

    except WebSocketDisconnect:
        logs.define_logger(logging.INFO, None, log_name, message=f"User '{current_user.username}' disconnected from project '{project_id}' chat.")
    except Exception as e:
        logs.define_logger(logging.ERROR, None, log_name, message=f"An error occurred in the chat WebSocket for user '{current_user.username}' on project '{project_id}': {e}")
    finally:
        # 7. Clean up the connection on disconnect or error
        await manager.disconnect(project_id, websocket)
        logs.define_logger(logging.INFO, None, log_name, message=f"Cleaned up connection for user '{current_user.username}' from project '{project_id}'.")
