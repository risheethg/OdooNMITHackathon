from app.repos.project_repo import ProjectRepo
from typing import Dict, Any, Optional
from app.models.project_model import Project, ProjectCreate, ProjectUpdate
from app.models.member_model import MemberUpdate
from app.core.logger import logs, logging, inspect
from app.repos.project_repo import project_repo # Import the singleton instance

class ProjectService:
    """
    Service layer for project-related operations.
    """
    def __init__(self, repo: ProjectRepo):
        self.repo = repo

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Service to retrieve a single project by its MongoDB _id."""
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Fetching project with ID: {project_id}")
        project_doc = self.repo.get_by_id(project_id)
        if project_doc:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Found project with ID: {project_id}")
            return Project.model_validate(project_doc)
        return None

    async def add_member_to_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Adds a new member to a project's team."""
        logs.define_logger(
            level=logging.INFO,
            loggName=inspect.stack()[0],
            message=f"Attempting to add user '{user_id}' to project '{project_id}'."
        )
        
        existing_project = self.repo.get_by_id(project_id)
        if not existing_project:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Add member failed: Project with ID '{project_id}' not found.")
            raise ValueError(f"Project with ID '{project_id}' not found.")
        
        if user_id in existing_project.get("members", []):
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"User '{user_id}' is already a member of project '{project_id}'. No change needed.")
            return Project(**existing_project)
        
        try:
            updated_doc = self.repo.add_member(project_id, user_id)
            if not updated_doc:
                # This case indicates the project was not found by the repo method,
                # but we already checked above. It's a defensive check.
                logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Failed to add member, could not retrieve project after update for '{project_id}'.")
                raise Exception("Failed to add member.")

            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully added user '{user_id}' to project '{project_id}'.")
            return Project.model_validate(updated_doc)
        except Exception as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred while adding member to project '{project_id}'. Error: {str(e)}")
            raise

    async def remove_member_from_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Removes a member from a project's team."""
        logs.define_logger(
            level=logging.INFO,
            loggName=inspect.stack()[0],
            message=f"Attempting to remove user '{user_id}' from project '{project_id}'."
        )

        existing_project = self.repo.get_by_id(project_id)
        if not existing_project:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Remove member failed: Project with ID '{project_id}' not found.")
            raise ValueError(f"Project with ID '{project_id}' not found.")
        
        if user_id not in existing_project.get("members", []):
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"User '{user_id}' is not a member of project '{project_id}'. No change needed.")
            return Project(**existing_project)
        
        try:
            updated_doc = self.repo.remove_member(project_id, user_id)
            if not updated_doc:
                logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Failed to remove member, could not retrieve project after update for '{project_id}'.")
                raise Exception("Failed to remove member.")

            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully removed user '{user_id}' from project '{project_id}'.")
            return Project.model_validate(updated_doc)
        except Exception as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred while removing member from project '{project_id}'. Error: {str(e)}")
            raise

# Dependency provider function
def get_project_service() -> ProjectService:
    return ProjectService(repo=project_repo)