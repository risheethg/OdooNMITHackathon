import os
import inspect
import logging
from functools import lru_cache
from jira import JIRA, JIRAError
from dotenv import load_dotenv

# Import your custom logger instance
from app.core.logger import logs

load_dotenv()


@lru_cache()
def get_jira_client() -> JIRA:
    """
    Initializes and returns a JIRA client instance.
    The connection is cached to avoid reconnecting on every request.
    Reads credentials from environment variables.
    """
    jira_url = os.getenv("JIRA_URL","")
    jira_username = os.getenv("JIRA_USERNAME","")
    jira_api_token = os.getenv("JIRA_API_TOKEN","")

    if not all([jira_url, jira_username, jira_api_token]):
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message="FATAL: Jira environment variables (JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN) are not set.")
        raise ConnectionError("Jira credentials are not configured in environment variables.")

    try:
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"Connecting to Jira at {jira_url}...")
        jira_client = JIRA(server=jira_url, basic_auth=(jira_username, jira_api_token))
        # Verify connection by fetching server info
        jira_client.server_info()
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message="Successfully connected to Jira.")
        return jira_client
    except JIRAError as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Failed to connect to Jira. Status: {e.status_code}, Error: {e.text}")
        raise ConnectionError(f"Could not connect to Jira: {e.text}")


def create_project(project_key: str, name: str, description: str):
    """
    Creates a new project in Jira.

    :param project_key: The unique key for the Jira project (e.g., 'PROJ').
    :param name: The full name of the project.
    :param description: The project's description.
    """
    log_message_prefix = f"Jira project creation for key '{project_key}'"
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Starting...")

    try:
        jira_client = get_jira_client()
        
        lead_account_id = jira_client.myself()['accountId']
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Using project lead account ID: {lead_account_id}")

        project_template_key = 'com.pyxis.greenhopper.jira:gh-simplified-scrum'

        jira_client.create_project(
            key=project_key,
            name=name,
            description=description,
            leadAccountId=lead_account_id,
            assigneeType='PROJECT_LEAD',
            projectTemplateKey=project_template_key
        )
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Successfully created.")
    except JIRAError as e:
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Failed. Status: {e.status_code}, Error: {e.text}")
        raise e


def delete_project(project_key: str):
    """
    Deletes a project from Jira permanently.

    :param project_key: The key of the project to delete.
    """
    log_message_prefix = f"Jira project deletion for key '{project_key}'"
    logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Starting...")

    try:
        jira_client = get_jira_client()
        jira_client.delete_project(key=project_key)
        logs.define_logger(level=logging.INFO, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Successfully deleted.")
    except JIRAError as e:
        if e.status_code == 404:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Project not found. It might have been already deleted.")
            return
        
        logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"{log_message_prefix}: Failed. Status: {e.status_code}, Error: {e.text}")
        raise e

