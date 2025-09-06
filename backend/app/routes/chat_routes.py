import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query, Body
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bson import ObjectId

from app.models.auth_model import User
from app.models.chat_model import GeminiRequest
from app.models.chat_model import ChatMessage, ChatMessageCreate
from app.services.auth_service import get_current_user_from_token, get_current_active_user, auth_repo
from app.services import chat_service
from app.core.logger import logs

router = APIRouter(tags=["Chat"])

class ConnectionManager:
    """Manages active WebSocket connections for project-specific chat rooms."""
    def __init__(self):
        # Structure: { "project_id": { "websocket_object": "username" } }
        self.active_connections: Dict[str, Dict[WebSocket, str]] = {}

    async def _send_personal_json(self, websocket: WebSocket, payload: Dict[str, Any]):
        """Sends a JSON payload to a single websocket client."""
        try:
            await websocket.send_json(payload)
        except Exception as e:
            logs.define_logger(logging.ERROR, message=f"Failed to send personal message: {e}")

    async def connect(self, websocket: WebSocket, project_id: str, user: User):
        """Accepts a new WebSocket connection and adds it to the project room."""
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = {}
        self.active_connections[project_id][websocket] = user.username
        # Announce user join
        await self.broadcast(project_id, {"event": "system_message", "data": {"message": f"User {user.username} has joined the chat."}})

    async def send_history(self, websocket: WebSocket, history: List[ChatMessage]):
        """Sends chat history to a newly connected client."""
        history_payload = {
            "event": "history",
            "data": [msg.model_dump(mode="json") for msg in history]
        }
        await self._send_personal_json(websocket, history_payload)


    def disconnect(self, websocket: WebSocket, project_id: str, username: str):
        """Removes a WebSocket connection from a project room."""
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                del self.active_connections[project_id][websocket]
                # If the room is empty, clean it up
                if not self.active_connections[project_id]:
                    del self.active_connections[project_id]

    async def broadcast(self, project_id: str, payload: Dict[str, Any]):
        """Broadcasts a JSON payload to all clients in a specific project room."""
        if project_id in self.active_connections:
            await asyncio.gather(
                *[
                    self._send_personal_json(ws, payload)
                    for ws in self.active_connections[project_id]
                ]
            )

manager = ConnectionManager()

@router.websocket("/ws/chat/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str, token: str = Query(...)):
    """
    WebSocket endpoint for real-time project chat.
    Authenticates user via token and checks for project membership.
    """
    user = None
    try:
        user = get_current_user_from_token(token)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token or user not found.")
            return

        # Centralized Authorization Check
        if not chat_service._is_user_project_member(project_id, user.user_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Forbidden: Not a project member.")
            return

        await manager.connect(websocket, project_id, user)

        # Send recent chat history to the newly connected user
        history = chat_service.get_chat_history(project_id, user.user_id, page=1, limit=50)
        await manager.send_history(websocket, history)

        while True:
            raw_data = await websocket.receive_text()
            message_data = json.loads(raw_data)
            
            # Create message via service (saves to DB)
            new_message = await chat_service.create_chat_message(
                project_id=project_id,
                user_id=user.user_id,
                username=user.username,
                data=ChatMessageCreate(message=message_data['message'])
            )
            
            # Broadcast the saved message object to all clients
            broadcast_payload = {"event": "new_message", "data": new_message.model_dump(mode="json")}
            await manager.broadcast(project_id, broadcast_payload)

    except WebSocketDisconnect:
        if user:
            manager.disconnect(websocket, project_id, user.username)
            await manager.broadcast(project_id, {"event": "system_message", "data": {"message": f"User {user.username} has left the chat."}})
    except Exception as e:
        logs.define_logger(logging.ERROR, message=f"Error in chat websocket: {e}")
        if websocket.client_state != WebSocketDisconnect:
             await websocket.close(code=status.WS_1011_INTERNAL_ERROR)