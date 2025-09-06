from app.repos.project_repo import ProjectRepo
from typing import Dict, Any, Optional

class ProjectService:
    """
    Service layer for project-related operations.
    """
    def __init__(self, project_repo: ProjectRepo):
        self.project_repo = project_repo

    def add_member_to_project(self, project_id: str, member: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Adds a team member to a project.
        """
        project = self.project_repo.find_one_by({"project_id": project_id})
        if not project:
            return None  # Project not found

        # You can add more business logic here, e.g., checking if the user exists
        return self.project_repo.add_team_member(project_id, member)

    def remove_member_from_project(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Removes a team member from a project.
        """
        project = self.project_repo.find_one_by({"project_id": project_id})
        if not project:
            return None  # Project not found

        # Additional checks, e.g., is the user the last admin?
        return self.project_repo.remove_team_member(project_id, user_id)