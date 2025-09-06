from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import logging
import inspect

# Your project's specific imports
from app.core.logger import logs

class ConnectionManager:
    """
    Manages active WebSocket connections for project-based chat rooms.
    This version is corrected to handle broadcasting to multiple clients per project.
    """
    def __init__(self):
        # A dictionary where keys are project_ids and values are lists of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        """
        Stores a new, already accepted WebSocket connection for a specific project.
        NOTE: This method NO LONGER calls `websocket.accept()`.
        """
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, project_id: str):
        """Removes a specific WebSocket connection from a project's list."""
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            # If no clients are left, clean up the project_id key
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def broadcast(self, project_id: str, data: dict):
        """Broadcasts a JSON message to all clients in a specific project room."""
        log_name = inspect.stack()[0]
        if project_id in self.active_connections:
            # We iterate over a copy of the list in case of disconnections during broadcast
            for connection in list(self.active_connections.get(project_id, [])):
                try:
                    await connection.send_json(data)
                except RuntimeError as e:
                    # This can happen if a client disconnects abruptly.
                    logs.define_logger(logging.WARNING, None, log_name, message=f"Failed to send to a client in project '{project_id}', likely disconnected. Error: {e}")
                    # The endpoint's finally block will handle the cleanup.
                    pass

# A single, shared instance for the entire application
manager = ConnectionManager()