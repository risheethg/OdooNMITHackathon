from fastapi import APIRouter, Depends, HTTPException, status

from app.models.member_model import MemberAdditionRequest, MemberRemovalRequest
from app.models.project_model import Project
from app.models.response import ResponseModel
from app.models.auth_model import User
from app.services.member_service import ProjectService, get_project_service
from app.services.auth_service import get_current_active_user
from app.services.project_service import get_project_by_id # To check ownership

router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["Project Members"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=ResponseModel[Project], status_code=status.HTTP_200_OK)
async def add_team_member_route(
    project_id: str, 
    member_request: MemberAdditionRequest, 
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_active_user)
):
    """Adds a team member to a project. Only the project creator can add members."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.created_by != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project creator can add members.")

    try:
        updated_project = service.add_member_to_project(project_id, member_request.user_id)
        return ResponseModel(status="success", message="Member added successfully.", data=updated_project)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/", response_model=ResponseModel[Project], status_code=status.HTTP_200_OK)
async def remove_team_member_route(
    project_id: str, 
    member_request: MemberRemovalRequest, 
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_active_user)
):
    """Removes a team member from a project. Only the project creator can remove members."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.created_by != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project creator can remove members.")

    try:
        updated_project = service.remove_member_from_project(project_id, member_request.user_id)
        return ResponseModel(status="success", message="Member removed successfully.", data=updated_project)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))