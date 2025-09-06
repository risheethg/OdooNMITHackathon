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

@router.websocket("/ws/notifications")
async def notification_websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for receiving real-time notifications.
    The channel is specific to the authenticated user.
    """
    log_name = inspect.stack()[0]
    current_user = auth_service.get_current_user_from_token(token)
    if not current_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # Accept the connection *after* successful authentication
    await websocket.accept()

    # The user_id serves as the unique channel for this user's notifications
    user_channel_id = current_user.user_id
    await manager.connect(websocket, user_channel_id)
    logs.define_logger(logging.INFO, None, log_name, message=f"Notification WebSocket connected for user '{current_user.username}'.")
    
    try:
        while True:
            # Keep the connection alive by waiting for messages (which we can ignore)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_channel_id)
        logs.define_logger(logging.INFO, None, log_name, message=f"Notification WebSocket disconnected for user '{current_user.username}'.")
