from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class WebSocketManager:
    """
    Manages active WebSocket connections for real-time broadcasting.
    This manager is designed for a multi-user, room-based system (e.g., a chat per project).
    """
    def __init__(self):
        # --- KEY CHANGE ---
        # The dictionary now maps a project_id (the "room") to a LIST of active connections.
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        """
        Accepts a new WebSocket connection and adds it to the list for a specific project.
        """
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        """
        Removes a WebSocket connection from a project's list.
        """
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            # If the room is empty, clean it up
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def broadcast(self, project_id: str, message_payload: dict):
        """
        Broadcasts a JSON message to all clients connected to a specific project.
        """
        if project_id in self.active_connections:
            # We use json.dumps here to ensure consistent formatting
            message_str = json.dumps(message_payload)
            
            # Iterate over a copy of the list in case of disconnections during broadcast
            for connection in self.active_connections[project_id][:]:
                try:
                    await connection.send_text(message_str)
                except (RuntimeError, WebSocketDisconnect):
                    # The client disconnected abruptly. Clean them up.
                    self.disconnect(connection, project_id)

# Create a single, shared instance for the entire application
manager = WebSocketManager()