import logging
import inspect
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from starlette import status
from starlette.websockets import WebSocketState

from app.utils.websocket_manager import manager
from app.core.logger import logs
from app.services import auth_service, chat_service
from app.models.chat_model import ChatMessageCreate
from app.models.auth_model import User

router = APIRouter(tags=["Websockets"])

@router.websocket("/ws/health-check")
async def websocket_health_check_endpoint(websocket: WebSocket):
    """
    A simple, unsecured WebSocket endpoint to verify basic connectivity.
    It accepts a connection, sends a welcome message, and echoes back any
    message it receives.
    """
    await websocket.accept()
    print("\n--- WebSocket Health Check: CONNECTION ACCEPTED ---")
    
    try:
        # Send an immediate confirmation message to the client
        await websocket.send_text("Connection successful. You are connected to the health check.")
        print("--- WebSocket Health Check: Welcome message sent. Awaiting client messages... ---")

        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            print(f"--- WebSocket Health Check: Received message: '{data}' ---")
            
            # Echo the message back to the client
            await websocket.send_text(f"Echo: {data}")
            print(f"--- WebSocket Health Check: Echoed message back to client. ---")

    except WebSocketDisconnect:
        print("--- WebSocket Health Check: Client disconnected cleanly. ---")
    except Exception as e:
        print(f"--- WebSocket Health Check: An unexpected error occurred: {e} ---")
    finally:
        # This block will run even if the client disconnects, ensuring we log it.
        print("--- WebSocket Health Check: Connection closed. ---")

@router.websocket("/ws/debug/chat/{project_id}")
async def debug_chat_websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...)
):
    """
    A temporary endpoint to debug the chat connection step-by-step.
    Step 1: Test Authentication.
    """
    print("\n--- DEBUGGER: WebSocket connection attempt received ---")
    await websocket.accept()
    print("--- DEBUGGER: Step 1 - Connection Accepted ---")

    current_user: User = None
    try:
        # --- TEST 1: AUTHENTICATION ---
        print(f"--- DEBUGGER: Step 2 - Attempting to authenticate with token: '{token[:20]}...' ---")
        current_user = auth_service.get_current_user_from_token(token)
        if not current_user:
            raise Exception("Token is valid, but no user was found.")
        
        print(f"--- DEBUGGER: Step 3 - AUTHENTICATION SUCCESSFUL. User: '{current_user.username}' (ID: {current_user.user_id}) ---")
        await websocket.send_json({
            "status": "success",
            "message": f"Authentication successful. Welcome, {current_user.username}!"
        })

        # --- TEST 2: AUTHORIZATION (SKIPPED) ---
        print("--- DEBUGGER: Step 4 - SKIPPING Authorization (project membership check) ---")

        # If we reach here, the problem is in the authorization step.
        print("--- DEBUGGER: Connection established successfully. Now in echo mode. ---")

        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo from debug: {data}")

    except Exception as e:
        print(f"--- DEBUGGER: AN ERROR OCCURRED: {e} ---")
        # Ensure we close the connection if an error occurs
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=1011, reason=f"Error during handshake: {e}")
    finally:
        print("--- DEBUGGER: Connection closed. ---")

@router.websocket("/ws/chat/{project_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...)
):
    """
    Handles real-time chat connections for a specific project.
    Authenticates, authorizes, and then manages the connection lifecycle.
    """
    log_name = inspect.stack()[0]
    current_user: User = None
    is_connection_active: bool = False

    # 1. Authenticate the user from the token before accepting the connection.
    try:
        current_user = auth_service.get_current_user_from_token(token)
        if not current_user:
            logs.define_logger(logging.WARNING, None, log_name, message="WebSocket connection rejected: Invalid token or user not found.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token or user not found.")
            return
    except Exception as e:
        logs.define_logger(logging.ERROR, None, log_name, message=f"An unexpected error occurred during WebSocket authentication: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication process failed.")
        return

    # 2. Authorize the user for the specific project.
    try:
        if not chat_service._is_user_project_member(project_id, current_user.user_id):
            logs.define_logger(logging.WARNING, None, log_name, message=f"WebSocket connection denied for user '{current_user.username}' to project '{project_id}'. Not a member.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Forbidden: Not a project member.")
            return
    except Exception as e:
        logs.define_logger(logging.ERROR, None, log_name, message=f"An error occurred during WebSocket authorization for user '{current_user.username}': {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Authorization process failed.")
        return

    # 3. If authentication and authorization succeed, accept the connection.
    try:
        await websocket.accept()
        await manager.connect(websocket, project_id)
        is_connection_active = True
        logs.define_logger(logging.INFO, None, log_name, message=f"WebSocket accepted for user '{current_user.username}' on project '{project_id}'.")
        
        # 4. Listen for incoming messages in a loop.
        while True:
            # FIX: Changed from receive_json() to receive_text() to handle plain text messages.
            message_text = await websocket.receive_text()

            # Ignore empty or whitespace-only messages
            if not message_text.strip():
                continue
            
            # 5. Save the message to the database via the service.
            message_data = ChatMessageCreate(message=message_text)
            new_message = chat_service.create_chat_message(
                project_id=project_id,
                user_id=current_user.user_id,
                username=current_user.username,
                data=message_data
            )
            
            # 6. Broadcast the new message to all clients in the project room.
            broadcast_payload = {"event": "new_message", "data": new_message.model_dump(mode="json")}
            await manager.broadcast(project_id, broadcast_payload)

    except WebSocketDisconnect:
        logs.define_logger(logging.INFO, None, log_name, message=f"User '{current_user.username}' disconnected from project '{project_id}' chat.")
    except Exception as e:
        logs.define_logger(logging.ERROR, None, log_name, message=f"An error occurred in the chat WebSocket for user '{current_user.username}' on project '{project_id}': {e}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        # 7. Clean up the connection ONLY if it was successfully established.
        if is_connection_active:
            await manager.disconnect(websocket, project_id)
            logs.define_logger(logging.INFO, None, log_name, message=f"Cleaned up connection for user '{current_user.username}' from project '{project_id}'.")
