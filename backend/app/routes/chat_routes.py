import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from typing import List, Dict
from bson import ObjectId

from app.models.auth_model import User
from app.services.auth_service import get_current_user_from_token, auth_repo
from app.services.project_service import get_project_by_id

router = APIRouter(tags=["Chat"])

class ConnectionManager:
    """Manages active WebSocket connections for project-specific chat rooms."""
    def __init__(self):
        # Structure: { "project_id": { "websocket_object": "username" } }
        self.active_connections: Dict[str, Dict[WebSocket, str]] = {}

    async def connect(self, websocket: WebSocket, project_id: str, user: User):
        """Accepts a new WebSocket connection and adds it to the project room."""
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = {}
        self.active_connections[project_id][websocket] = user.username
        # Announce user join
        await self.broadcast(f"User {user.username} has joined the chat.", project_id, is_system_message=True)

    def disconnect(self, websocket: WebSocket, project_id: str, username: str):
        """Removes a WebSocket connection from a project room."""
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                del self.active_connections[project_id][websocket]
                # If the room is empty, clean it up
                if not self.active_connections[project_id]:
                    del self.active_connections[project_id]

    async def broadcast(self, message: str, project_id: str, is_system_message: bool = False):
        """Broadcasts a message to all clients in a specific project room."""
        if project_id in self.active_connections:
            # Use asyncio.gather for concurrent sending
            await asyncio.gather(
                *[
                    ws.send_json({"message": message, "is_system": is_system_message})
                    for ws in self.active_connections[project_id]
                ]
            )

    async def broadcast_user_message(self, message: str, project_id: str, username: str):
        """Broadcasts a message from a specific user."""
        if project_id in self.active_connections:
            await asyncio.gather(
                *[
                    ws.send_json({"message": message, "username": username, "is_system": False})
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
    user = get_current_user_from_token(token)
    project = get_project_by_id(project_id)

    if not user or not project or ObjectId(user.user_id) not in project.members:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, project_id, user)
    username = user.username
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_user_message(data, project_id, username)
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id, username)
        await manager.broadcast(f"User {username} has left the chat.", project_id, is_system_message=True)