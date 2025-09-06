from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from app.models.task_model import Task, TaskCreate, TaskUpdate
from app.models.response import ResponseModel
from app.repos.task_repo import TaskRepo
from app.services.task_service import (
    create_task, 
    get_task, 
    get_tasks_for_project, 
    update_task, 
    delete_task
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Route to create a new task
@router.post("/", response_model=ResponseModel[Task], status_code=status.HTTP_201_CREATED)
def create_new_task(project_id: str, task_data: TaskCreate):
    """
    Creates a new task for a specified project.
    """
    try:
        new_task = create_task(project_id, task_data)
        return ResponseModel(
            status="success",
            message="Task created successfully.",
            status_code=status.HTTP_201_CREATED,
            data=new_task
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

# Route to get a single task by ID
@router.get("/{task_id}", response_model=ResponseModel[Optional[Task]], status_code=status.HTTP_200_OK)
def get_task_by_id(task_id: str):
    """
    Retrieves a single task by its ID.
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    
    return ResponseModel(
        status="success",
        message="Task fetched successfully.",
        status_code=status.HTTP_200_OK,
        data=task
    )

# Route to get all tasks for a project
@router.get("/project/{project_id}", response_model=ResponseModel[List[Task]], status_code=status.HTTP_200_OK)
def get_all_tasks_for_project(project_id: str):
    """
    Retrieves all tasks for a specific project.
    """
    tasks = get_tasks_for_project(project_id)
    return ResponseModel(
        status="success",
        message="Tasks fetched successfully.",
        status_code=status.HTTP_200_OK,
        data=tasks
    )

# Route to update an existing task
@router.put("/{task_id}", response_model=ResponseModel[Task], status_code=status.HTTP_200_OK)
def update_existing_task(task_id: str, task_update: TaskUpdate):
    """
    Updates an existing task by its ID.
    """
    try:
        updated_task = update_task(task_id, task_update)
        if not updated_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or no changes made.")
        
        return ResponseModel(
            status="success",
            message="Task updated successfully.",
            status_code=status.HTTP_200_OK,
            data=updated_task
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

# Route to delete a task
@router.delete("/{task_id}", response_model=ResponseModel[str], status_code=status.HTTP_200_OK)
def delete_existing_task(task_id: str):
    """
    Deletes a task by its ID (soft delete).
    """
    is_deleted = delete_task(task_id)
    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or already deleted.")
    
    return ResponseModel(
        status="success",
        message="Task deleted successfully.",
        status_code=status.HTTP_200_OK,
        data=f"Task with ID {task_id} has been soft-deleted."
    )