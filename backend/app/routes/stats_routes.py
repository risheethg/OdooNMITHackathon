from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.response import ResponseModel
from app.models.auth_model import User
from app.services import stats_service
from app.services.auth_service import get_current_active_user
from app.services.chat_service import _is_user_project_member

router = APIRouter(
    prefix="/stats",
    tags=["Statistics"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/overview", response_model=ResponseModel[Dict[str, Any]])
def get_global_stats():
    """
    Provides a high-level overview of application-wide statistics.
    (This could be restricted to admin users in a real application).
    """
    stats = stats_service.get_global_overview_stats()
    return ResponseModel(status="success", data=stats, status_code=status.HTTP_200_OK)

@router.get("/user/me", response_model=ResponseModel[Dict[str, Any]])
def get_my_user_stats(current_user: User = Depends(get_current_active_user)):
    """
    Provides statistics related to the currently authenticated user.
    """
    stats = stats_service.get_user_overview_stats(current_user.user_id)
    return ResponseModel(status="success", data=stats, status_code=status.HTTP_200_OK)

@router.get("/project/{project_id}", response_model=ResponseModel[Dict[str, Any]])
def get_project_dashboard(project_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Provides detailed statistics for a specific project dashboard.
    Requires the user to be a member of the project.
    """
    # Authorization check: Ensure user is a member of the project
    if not _is_user_project_member(project_id, current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project."
        )

    try:
        stats = stats_service.get_project_dashboard_stats(project_id)
        return ResponseModel(status="success", data=stats, status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))