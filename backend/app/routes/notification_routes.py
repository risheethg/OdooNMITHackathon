from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Query, WebSocketDisconnect
from typing import List

from app.models.response import ResponseModel
from app.models.auth_model import User
from app.models.notification_model import Notification
from app.services import notification_service, auth_service
from app.utils.websocket_manager import manager

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    dependencies=[Depends(auth_service.get_current_active_user)]
)

@router.get("/", response_model=ResponseModel[List[Notification]])
def get_user_notifications(current_user: User = Depends(auth_service.get_current_active_user)):
    """Retrieve the current user's notifications."""
    notifications = notification_service.get_notifications_for_user(current_user.user_id)
    return ResponseModel(
        status="success",
        message="Notifications retrieved successfully.",
        status_code=status.HTTP_200_OK,
        data=notifications
    )

@router.patch("/{notification_id}/read", response_model=ResponseModel)
def mark_as_read(notification_id: str, current_user: User = Depends(auth_service.get_current_active_user)):
    """Mark a specific notification as read."""
    success = notification_service.mark_notification_as_read(notification_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found or you do not have permission.")
    
    return ResponseModel(
        status="success",
        message="Notification marked as read.",
        status_code=status.HTTP_200_OK
    )
