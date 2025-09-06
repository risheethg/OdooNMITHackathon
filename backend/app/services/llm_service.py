import logging
import inspect
from typing import List, Dict, Any

from app.core.logger import logs
from app.core.llm_connection import get_gemini_client
from app.models.chat_model import ChatMessage
from app.models.task_model import TaskStatus
from app.repos.project_repo import project_repo
from app.repos.task_repo import task_repo

GEMINI_MODEL_NAME = "gemini-2.5-flash" # Or "gemini-1.5-pro-latest" if you have access

async def generate_gemini_response(
    project_id: str,
    chat_history: List[ChatMessage],
    user_query: str
) -> str:
    """
    Generates a response from the Gemini LLM based on project context and chat history.
    """
    log_name = inspect.stack()[0]
    logs.define_logger(logging.INFO, None, log_name, message=f"Generating Gemini response for project '{project_id}' with query: '{user_query}'")

    try:
        gemini_client = get_gemini_client()

        # 1. Get Project Context
        project_doc = project_repo.get_by_id(project_id)
        project_name = project_doc.get("project_name", "Unknown Project")
        project_description = project_doc.get("description", "No description provided.")

        # 2. Get Task Context
        tasks = task_repo.get_by_project_id(project_id)
        task_summary = "\n".join(
            [f"- Task: '{t.get('title')}', Status: {t.get('status', 'N/A')}, Assignee: {t.get('assignee', 'N/A')}" for t in tasks]
        )
        if not task_summary:
            task_summary = "No tasks have been created for this project yet."

        # 3. Build System Prompt with all context
        system_prompt = (
            f"You are an AI assistant named Gemini, designed to help with project management and collaboration within the '{project_name}' project. "
            f"The project is described as: '{project_description}'. "
            "\n\nHere is a summary of the current tasks in this project:\n"
            f"{task_summary}\n\n"
            "Your goal is to provide helpful, concise, and relevant answers based on the project context and chat history. "
            "Keep your responses professional and to the point. If you don't know the answer, state that you cannot provide it."
        )

        # 4. Initialize the model WITH the system prompt
        model = gemini_client.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            system_instruction=system_prompt
        )

        # 5. Format Chat History for Context
        # Gemini's chat history format is a list of dicts with 'role' and 'parts'
        formatted_history = []
        for msg in chat_history:
            # Map your user/Gemini to 'user'/'model' roles
            role = "user" if msg.username != "Gemini AI" else "model"
            formatted_history.append({"role": role, "parts": [msg.message]})

        # Add the current user's query
        formatted_history.append({"role": "user", "parts": [user_query]})

        # 6. Generate Content
        # Start a chat session with the model
        chat_session = model.start_chat(history=formatted_history[:-1]) # Exclude the last user query from initial history
        response = await chat_session.send_message_async(user_query)

        # Extract text response
        gemini_response_text = response.text
        logs.define_logger(logging.INFO, None, log_name, message=f"Gemini response generated: {gemini_response_text[:100]}...")
        return gemini_response_text

    except Exception as e:
        logs.define_logger(logging.ERROR, None, log_name, message=f"Error generating Gemini response: {e}")
        # Return a fallback message or re-raise a custom exception
        return "I'm sorry, I couldn't process your request at this moment. Please try again later."