import logging
import inspect
from typing import List, Dict, Any, Optional

# Import the custom logger instance
from app.core.logger import logs

# Import our refactored components
from app.repos.project_repo import project_repo
from app.services import jira_service
from app.models.project_model import Project, ProjectCreate, ProjectUpdate

def create_project(project_data: ProjectCreate, user_id: str) -> Project: # <-- ADDED user_id PARAMETER
    """
    Orchestrates creating a project in our database and in Jira.
    """
    logs.define_logger(
        level=logging.INFO,
        loggName=inspect.stack()[0],
        message=f"Attempting to create a new project with name: '{project_data.project_name}' by user: '{user_id}'"
    )
    
    # Check if a project with the same name already exists
    if project_repo.get_by_name(project_data.project_name):
        logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Project creation failed: Name '{project_data.project_name}' already exists.")
        raise ValueError(f"A project with the name '{project_data.project_name}' already exists.")

    try:
        # 1. Generate the Jira Project Key
        jira_key = ''.join(filter(str.isalnum, project_data.project_name))[:5].upper()
        logs.define_logger(level=logging.DEBUG, loggName=inspect.stack()[0], message=f"Generated Jira key: '{jira_key}'")

        # 2. Call the Jira service to create the project in Jira
        jira_creation_success = False
        try:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to create project in Jira with key: '{jira_key}'")
            jira_service.create_project(
                project_key=jira_key,
                name=project_data.project_name,
                description=project_data.description or ""
            )
            jira_creation_success = True
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message="Successfully created project in Jira.")
        except Exception as e:
            logs.define_logger(
                level=logging.WARNING,
                loggName=inspect.stack()[0],
                message=f"Failed to create project in Jira. Proceeding with local creation only. Error: {str(e)}"
            )

        # 3. Prepare and save the project in our database
        project_dict = project_data.model_dump()
        project_dict['created_by'] = user_id  # <-- ADDED USER ID TO THE DOCUMENT
        if jira_creation_success:
            project_dict['jira_project_key'] = jira_key
        
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message="Creating project in local database.")
        inserted_id = project_repo.create(project_dict)
        
        # 4. Return the newly created project document
        new_project_doc = project_repo.get_by_id(str(inserted_id))
        if not new_project_doc:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"FATAL: Failed to retrieve project with id '{inserted_id}' immediately after creation.")
            raise Exception("Failed to retrieve project after creation.")
        
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully created project with ID: {inserted_id}")
        return Project(**new_project_doc)
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred during project creation. Error: {str(e)}")
        raise

# ... (rest of the service file remains the same) ...

def get_all_projects(user_id: str) -> List[Project]: # <-- MODIFIED
    """
    Service to retrieve all projects a user is associated with (either as creator or member).
    """
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Fetching all projects for user ID: {user_id}")
    try:
        # MongoDB query to find documents where the user is the creator OR is in the members array
        query = {
            "$or": [
                {"created_by": user_id},
                {"members": user_id}
            ]
        }
        project_docs = project_repo.get_all(query) # Use the get_all method from the new BaseRepo
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully retrieved {len(project_docs)} projects for user {user_id}.")
        return [Project(**doc) for doc in project_docs]
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Failed to fetch projects for user {user_id}. Error: {str(e)}")
        raise

def get_project_by_id(project_id: str) -> Optional[Project]:
    """Service to retrieve a single project by its MongoDB _id."""
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Fetching project with ID: {project_id}")
    try:
        project_doc = project_repo.get_by_id(project_id)
        if project_doc:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Found project with ID: {project_id}")
            return Project(**project_doc)
        else:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Project with ID: {project_id} not found.")
            return None
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Error fetching project with ID: {project_id}. Error: {str(e)}")
        raise

def update_project(project_id: str, project_update: ProjectUpdate) -> Optional[Project]:
    """Service to update a project."""
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to update project with ID: {project_id}")
    try:
        update_dict = project_update.model_dump(exclude_unset=True)
        if not update_dict:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message="Update operation cancelled: No update data provided.")
            raise ValueError("No update data provided.")
            
        modified_count = project_repo.update(project_id, update_dict)
        if modified_count > 0:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully updated project with ID: {project_id}")
            return get_project_by_id(project_id)
        else:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Project with ID: {project_id} not found or no changes were made.")
            return None
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Error updating project with ID: {project_id}. Error: {str(e)}")
        raise

def delete_project(project_id: str) -> bool:
    """
    Orchestrates deleting a project from our database (soft delete) and from Jira.
    """

    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to delete project with ID: {project_id}")
    try:
        project_to_delete = get_project_by_id(project_id)
        if not project_to_delete:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Cannot delete. Project with ID '{project_id}' not found.")
            raise ValueError(f"Project with ID '{project_id}' not found.")

        if project_to_delete.jira_project_key:
            try:
                logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to delete Jira project with key: {project_to_delete.jira_project_key}")
                jira_service.delete_project(project_key=project_to_delete.jira_project_key)
                logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message="Successfully deleted Jira project.")
            except Exception as e:
                logs.define_logger(
                    level=logging.WARNING,
                    loggName=inspect.stack()[0],
                    message=f"Failed to delete Jira project {project_to_delete.jira_project_key}, but proceeding with local soft delete. Error: {str(e)}"
                )

        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Soft-deleting project with ID: {project_id} from local database.")
        modified_count = project_repo.delete_soft(project_id)
        
        if modified_count > 0:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully soft-deleted project ID: {project_id}")
        else:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Soft delete failed for project ID: {project_id}. Project may have already been deleted.")

        return modified_count > 0
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred during project deletion for ID: {project_id}. Error: {str(e)}")
        raise
