from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

# Import the models for projects, users, and responses
from ..models.project_model import Project, ProjectCreate, ProjectUpdate
from ..models.auth_model import User
from ..models.response import ResponseModel

# Import the services for projects and authentication
from ..services import project_service
from ..services.auth_service import get_current_active_user

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    # Add a dependency here to protect all routes in this router
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
def create_new_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user) # Dependency also confirms user is active
):
    """
    Create a new project. Requires authentication.
    """
    try:
        new_project = project_service.create_project(project_data, current_user.user_id)
        return ResponseModel(
            status="Success",
            message="Project created successfully.",
            data=new_project.model_dump(by_alias=True),
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.get("/", response_model=ResponseModel)
def get_all_user_projects(current_user: User = Depends(get_current_active_user)):
    """
    Retrieve all non-deleted projects. Requires authentication.
    """
    projects = project_service.get_all_projects(current_user.user_id)
    projects_data = [p.model_dump(by_alias=True) for p in projects]
    return ResponseModel(
        status="Success",
        message="Projects retrieved successfully.",
        data={"projects": projects_data},
        status_code=status.HTTP_200_OK
    )


@router.get("/{project_id}", response_model=ResponseModel)
def get_single_project(project_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Retrieve a single project by its ID. Requires authentication.
    """
    project = project_service.get_project_by_id(project_id)
    if not project:
        return ResponseModel(
            status="Failure",
            message="Project not found.",
            data=None,
            status_code=status.HTTP_404_NOT_FOUND
        )
    return ResponseModel(
        status="Success",
        message="Project retrieved successfully.",
        data=project.model_dump(by_alias=True),
        status_code=status.HTTP_200_OK
    )


@router.put("/{project_id}", response_model=ResponseModel)
def update_existing_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a project's details. Requires authentication.
    """
    try:
        updated_project = project_service.update_project(project_id, project_update)
        if not updated_project:
            return ResponseModel(
                status="Failure",
                message="Project not found or no changes made.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )
        return ResponseModel(
            status="Success",
            message="Project updated successfully.",
            data=updated_project.model_dump(by_alias=True),
            status_code=status.HTTP_200_OK
        )
    except ValueError as ve:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.delete("/{project_id}", response_model=ResponseModel)
def delete_a_project(project_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Soft-delete a project. Requires authentication.
    """
    try:
        success = project_service.delete_project(project_id)
        if not success:
            return ResponseModel(
                status="Failure",
                message="Project not found or could not be deleted.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )
        return ResponseModel(
            status="Success",
            message="Project deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK
        )
    except ValueError as ve:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
