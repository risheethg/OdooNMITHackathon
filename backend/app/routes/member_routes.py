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
    # It's better to use the service to get the project to maintain consistency
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    if project.created_by != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project creator can add members.")

    try:
        updated_project = await service.add_member_to_project(project_id, member_request.user_id)
        if not updated_project:
            raise ValueError("Failed to add member or find project.")
            
        return ResponseModel(
            status="success", 
            message="Member added successfully.", 
            data=updated_project,
            status_code=status.HTTP_200_OK # Add this line
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{user_id}", response_model=ResponseModel[Project], status_code=status.HTTP_200_OK)
async def remove_team_member_route(
    project_id: str, 
    user_id: str, # <-- user_id is now a path parameter
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_active_user)
):
    """Removes a team member from a project. Only the project creator can remove members."""
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.created_by != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project creator can remove members.")

    try:
        # This service call should use `update_one` with `$pull` to remove the member
        updated_project = await service.remove_member_from_project(project_id, user_id)
        if not updated_project:
            raise ValueError("Failed to remove member or find project.")
        
        # --- THE FIX IS HERE ---
        # The `status_code` field was also missing from this ResponseModel instance.
        return ResponseModel(
            status="success", 
            message="Member removed successfully.", 
            data=updated_project,
            status_code=status.HTTP_200_OK # Add this line
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))