import logging
import inspect
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.logger import logs
from app.repos.task_repo import task_repo
from app.models.task_model import Task, TaskCreate, TaskUpdate
from app.repos.project_repo import project_repo
from app.services import notification_service # Import the new service

# Assume task_repo and project_repo are instantiated and configured
# task_repo = TaskRepo(collection=db.tasks)
# project_repo = ProjectRepo(collection=db.projects)

def _is_user_valid_for_assignment(project_id: str, user_id: str) -> bool:
    """
    Checks if a user can be assigned a task in a project.
    The user must be the project creator or a member.
    """
    project = project_repo.get_by_id(project_id)
    if not project:
        return False # Project doesn't exist, so assignment is invalid.

    # Check if the user is the creator
    if project.get("created_by") == user_id:
        return True
    
    # Check if the user is in the members list
    return user_id in project.get("members", [])


async def create_task(project_id: str, task_data: TaskCreate, creator_id: str) -> Task:
    """
    Creates a new task within a specified project.
    """
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to create a new task for project ID: {project_id}")

    # Ensure the project exists before creating the task
    project = project_repo.get_by_id(project_id)
    if not project:
        logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Task creation failed: Project with ID '{project_id}' does not exist.")
        raise ValueError(f"Project with ID '{project_id}' not found.")

    # Validate that the assignee is a member of the project
    if not _is_user_valid_for_assignment(project_id, task_data.assignee):
        logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Task creation failed: Assignee '{task_data.assignee}' is not a member of project '{project_id}'.")
        raise ValueError(f"Assignee with ID '{task_data.assignee}' is not a valid member of this project.")

    try:
        task_dict = task_data.model_dump()
        task_dict['project_id'] = project_id
        # Set the creator ID from the authenticated user
        task_dict['created_by'] = creator_id
        task_dict['created_at'] = datetime.utcnow()
        task_dict['updated_at'] = datetime.utcnow()
        
        new_task_doc = task_repo.create_task(data=task_dict)
        if not new_task_doc:
            raise Exception("Failed to create or retrieve the new task.")
        
        new_task = Task.model_validate(new_task_doc)
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully created new task with ID: {new_task.task_id}")
        
        # --- NOTIFICATION ---
        # Create a notification for the assignee
        await notification_service.create_notification(
            user_id=new_task.assignee,
            message=f"You have been assigned a new task: '{new_task.title}'"
        )
        return new_task
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred during task creation. Error: {str(e)}")
        raise

def get_task(task_id: str) -> Optional[Task]:
    """
    Retrieves a single task by its ID.
    """
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Fetching task with ID: {task_id}")
    task_doc = task_repo.get_by_id(task_id)
    if not task_doc:
        logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Task with ID '{task_id}' not found.")
        return None
    
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully fetched task ID: {task_id}")
    return Task.model_validate(task_doc)

def get_tasks_for_project(project_id: str) -> List[Task]:
    """
    Retrieves all tasks for a specific project.
    """
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Fetching tasks for project ID: {project_id}")
    task_docs = task_repo.get_by_project_id(project_id)
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Found {len(task_docs)} tasks for project ID: {project_id}")
    return [Task.model_validate(doc) for doc in task_docs]

async def update_task(task_id: str, task_update: TaskUpdate) -> Optional[Task]:
    """
    Updates an existing task by its ID.
    """
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to update task ID: {task_id}")
    
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Update operation cancelled for task ID '{task_id}': No update data provided.")
        raise ValueError("No update data provided.")
    
    # If the assignee is being updated, validate the new assignee
    if 'assignee' in update_data:
        task_doc = task_repo.get_by_id(task_id)
        if not task_doc:
            raise ValueError(f"Task with ID '{task_id}' not found.")
        project_id = task_doc.get("project_id")
        if not _is_user_valid_for_assignment(project_id, update_data['assignee']):
            raise ValueError(f"New assignee with ID '{update_data['assignee']}' is not a valid member of the project.")

    update_data['updated_at'] = datetime.utcnow()
    
    try:
        updated_task_doc = task_repo.update_task(task_id, update_data)
        if not updated_task_doc:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Task with ID '{task_id}' not found for update.")
            return None
        
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully updated task ID: {task_id}")
        updated_task = Task.model_validate(updated_task_doc)

        # --- NOTIFICATION ---
        # If the assignee was changed, notify the new assignee
        if 'assignee' in update_data:
            await notification_service.create_notification(user_id=updated_task.assignee, message=f"A task has been assigned to you: '{updated_task.title}'")

        return updated_task
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred during task update for ID: {task_id}. Error: {str(e)}")
        raise

def delete_task(task_id: str) -> bool:
    """
    Soft deletes a task by its ID.
    """
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Attempting to soft-delete task with ID: {task_id}")
    
    task_exists = task_repo.get_by_id(task_id)
    if not task_exists:
        logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Task with ID '{task_id}' not found for deletion.")
        return False
        
    try:
        is_deleted = task_repo.delete_task(task_id)
        if is_deleted:
            logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Successfully soft-deleted task ID: {task_id}")
        else:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Task with ID '{task_id}' was not deleted. It might have already been deleted or not found.")
        return is_deleted
    except Exception as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"An unexpected error occurred during task deletion for ID: {task_id}. Error: {str(e)}")
        raise