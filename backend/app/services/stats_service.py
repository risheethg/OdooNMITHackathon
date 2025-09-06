from typing import Dict, Any
from app.repos.auth_repo import auth_repo
from app.repos.project_repo import project_repo
from app.repos.task_repo import task_repo
from app.models.task_model import TaskStatus


def get_global_overview_stats() -> Dict[str, Any]:
    """
    Calculates high-level statistics for the entire application.
    Note: In a large-scale app, these counts might be cached.
    """
    total_users = auth_repo.collection.count_documents({"is_deleted": False})
    total_projects = project_repo.collection.count_documents({"is_deleted": False})
    total_tasks = task_repo.collection.count_documents({"is_deleted": False})

    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
    }


def get_user_overview_stats(user_id: str) -> Dict[str, Any]:
    """
    Calculates statistics specific to a single user.
    """
    # Count projects user is a member of or created
    projects_count = project_repo.collection.count_documents({
        "$or": [{"created_by": user_id}, {"members": user_id}],
        "is_deleted": False
    })

    # Count tasks assigned to the user
    assigned_tasks_count = task_repo.collection.count_documents({
        "assignee": user_id,
        "is_deleted": False
    })

    # Get breakdown of assigned tasks by status
    pipeline = [
        {"$match": {"assignee": user_id, "is_deleted": False}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    task_status_breakdown = {item['_id']: item['count'] for item in task_repo.collection.aggregate(pipeline)}

    return {
        "projects_count": projects_count,
        "assigned_tasks_count": assigned_tasks_count,
        "task_status_breakdown": task_status_breakdown,
    }


def get_project_dashboard_stats(project_id: str) -> Dict[str, Any]:
    """
    Calculates detailed statistics for a single project dashboard.
    """
    project = project_repo.get_by_id(project_id)
    if not project:
        raise ValueError("Project not found")

    member_count = len(project.get("members", [])) + 1  # +1 for the creator

    total_tasks_in_project = task_repo.collection.count_documents({
        "project_id": project_id,
        "is_deleted": False
    })

    # Get breakdown of project tasks by status
    pipeline = [
        {"$match": {"project_id": project_id, "is_deleted": False}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    task_status_breakdown = {item['_id']: item['count'] for item in task_repo.collection.aggregate(pipeline)}

    return {
        "member_count": member_count,
        "total_tasks_in_project": total_tasks_in_project,
        "task_status_breakdown": task_status_breakdown,
    }