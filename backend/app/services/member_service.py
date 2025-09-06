from app.repos.project_repo import ProjectRepo
from typing import Dict, Any, Optional
from app.models.project_model import Project, ProjectCreate, ProjectUpdate, MemberUpdate
from app.core.logger import logs, logging, inspect
from app.repos.project_repo import project_repo

class ProjectService:
    """
    Service layer for project-related operations.
    """
    def add_member_to_project(project_id: str, user_id: str) -> Project:
        """Adds a new member to a project's team."""
        logs.define_logger(
            level=logging.INFO,
            loggName=inspect.stack()[0],
            message=f"Attempting to add user '{user_id}' to project '{project_id}'."
        )
        
        existing_project = project_repo.get_by_id(project_id)
        if not existing_project:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Add member failed: Project with ID '{project_id}' not found.")
            raise ValueError(f"Project with ID '{project_id}' not found.")
        
        if user_id in existing_project.get("members", []):
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"User '{user_id}' is already a member of project '{project_id}'. No change needed.")
            return Project(**existing_project)
        
        try:
            updated_doc = project_repo.add_member(project_id, user_id)
            if not updated_doc:
                # This case indicates the project was not found by the repo method,
                # but we already checked above. It's a defensive check.
                logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Failed to add member, could not retrieve project after update for '{project_id}'.")
                raise Exception("Failed to add member.")

            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully added user '{user_id}' to project '{project_id}'.")
            return Project(**updated_doc)
        except Exception as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred while adding member to project '{project_id}'. Error: {str(e)}")
            raise

    def remove_member_from_project(project_id: str, user_id: str) -> Project:
        """Removes a member from a project's team."""
        logs.define_logger(
            level=logging.INFO,
            loggName=inspect.stack()[0],
            message=f"Attempting to remove user '{user_id}' from project '{project_id}'."
        )

        existing_project = project_repo.get_by_id(project_id)
        if not existing_project:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Remove member failed: Project with ID '{project_id}' not found.")
            raise ValueError(f"Project with ID '{project_id}' not found.")
        
        if user_id not in existing_project.get("members", []):
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"User '{user_id}' is not a member of project '{project_id}'. No change needed.")
            return Project(**existing_project)
        
        try:
            updated_doc = project_repo.remove_member(project_id, user_id)
            if not updated_doc:
                logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Failed to remove member, could not retrieve project after update for '{project_id}'.")
                raise Exception("Failed to remove member.")

            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully removed user '{user_id}' from project '{project_id}'.")
            return Project(**updated_doc)
        except Exception as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred while removing member from project '{project_id}'. Error: {str(e)}")
            raise