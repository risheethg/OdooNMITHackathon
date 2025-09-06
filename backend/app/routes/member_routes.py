from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.mongo_client import MongoClient

from app.models.member_model import MemberAdditionRequest, MemberRemovalRequest
from app.models.project_model import Project
from app.services.member_service import ProjectService
from app.repos.project_repo import ProjectRepo

# Assume you have a global MongoDB client and collections setup
# For simplicity, let's represent the dependency injection here
def get_project_service() -> ProjectService:
    # This is a simplified dependency injection setup
    client = MongoClient("mongodb://localhost:27017/") # Replace with your URI
    db = client.synergysphere_db
    project_collection = db.projects
    project_repo = ProjectRepo(collection=project_collection)
    return ProjectService(project_repo=project_repo)

router = APIRouter()

@router.post("/projects/{project_id}/members", response_model=Project, status_code=status.HTTP_200_OK)
def add_team_member_route(project_id: str, member_request: MemberAdditionRequest, service: ProjectService = Depends(get_project_service)):
    """
    Adds a team member to a project.
    """
    member_data = member_request.model_dump()
    updated_project = service.add_member_to_project(project_id, member_data)
    if not updated_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return updated_project

@router.delete("/projects/{project_id}/members", response_model=Project, status_code=status.HTTP_200_OK)
def remove_team_member_route(project_id: str, member_request: MemberRemovalRequest, service: ProjectService = Depends(get_project_service)):
    """
    Removes a team member from a project.
    """
    updated_project = service.remove_member_from_project(project_id, member_request.user_id)
    if not updated_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return updated_project