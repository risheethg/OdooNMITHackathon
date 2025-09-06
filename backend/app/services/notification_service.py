import logging
import inspect
from typing import List, Optional

from app.core.logger import logs
from app.repos.notification_repo import notification_repo
from app.models.notification_model import Notification, NotificationStatus
from app.utils.websocket_manager import manager

async def create_notification(user_id: str, message: str, link: Optional[str] = None) -> Notification:
    """
    Creates a notification, saves it to the DB, and pushes it via WebSocket.
    """
    logs.define_logger(logging.INFO, None, inspect.stack()[0], message=f"Creating notification for user '{user_id}': {message}")
    
    notification_data = {
        "user_id": user_id,
        "message": message,
        "link": link,
        "status": NotificationStatus.UNREAD.value
    }
    
    inserted_id = notification_repo.create(notification_data)
    new_notification_doc = notification_repo.get_by_id(str(inserted_id))
    
    if not new_notification_doc:
        raise Exception("Failed to create or retrieve notification.")
        
    notification = Notification.model_validate(new_notification_doc)
    
    # Push the notification to the user via WebSocket
    # We use the user_id as the "project_id" for the broadcast channel
    broadcast_payload = {"event": "new_notification", "data": notification.model_dump(mode="json")}
    await manager.broadcast(user_id, broadcast_payload)
    logs.define_logger(logging.INFO, None, inspect.stack()[0], message=f"Pushed notification '{notification.notification_id}' to user '{user_id}'.")
    
    return notification

def get_notifications_for_user(user_id: str) -> List[Notification]:
    """Retrieves all notifications for a specific user."""
    notification_docs = notification_repo.get_by_user_id(user_id)
    return [Notification.model_validate(doc) for doc in notification_docs]

def mark_notification_as_read(notification_id: str, user_id: str) -> bool:
    """Marks a specific notification as read, ensuring it belongs to the user."""
    notification = notification_repo.get_by_id(notification_id)
    if notification and notification.get("user_id") == user_id:
        return notification_repo.mark_as_read(notification_id) > 0
    return False