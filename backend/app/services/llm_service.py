import asyncio
from datetime import datetime, timezone
import logging

from app.routes.chat_routes import manager as chat_manager
from app.services import chat_service
from app.models.chat_model import ChatMessageCreate
from app.core.llm_connection import get_gemini_client
from app.repos.project_repo import project_repo
from app.repos.task_repo import task_repo
from app.core.logger import logs

async def handle_gemini_prompt(project_id: str, prompt: str, user_id: str, username: str):
    """
    Handles a prompt for the Gemini LLM, saves the interaction to the chat history,
    and broadcasts the response.

    Args:
        project_id: The ID of the project where the prompt was made.
        prompt: The user's prompt text.
        user_id: The ID of the user who made the prompt.
        username: The username of the user.
    """
    # 1. Save and broadcast the user's prompt to the chat.
    # This uses the existing chat service, which will verify the user's membership.
    user_prompt_message = await chat_service.create_chat_message(
        project_id=project_id,
        user_id=user_id,
        username=username,
        data=ChatMessageCreate(message=f"@gemini {prompt}")
    )
    await chat_manager.broadcast(project_id, {"event": "new_message", "data": user_prompt_message.model_dump(mode="json")})

    # 2. Gather context for the LLM
    try:
        project = project_repo.get_by_id(project_id)
        tasks = task_repo.get_by_project_id(project_id)
        chat_history = chat_service.get_chat_history(project_id, user_id, page=1, limit=20)

        # Format the context into a string for the LLM
        context_str = f"Project Name: {project.get('project_name')}\n"
        context_str += f"Project Description: {project.get('description', 'N/A')}\n\n"
        context_str += "Tasks:\n"
        if tasks:
            for task in tasks:
                context_str += f"- {task.get('title')} (Status: {task.get('status')})\n"
        else:
            context_str += "- No tasks found.\n"
        
        context_str += "\nRecent Chat History:\n"
        if chat_history:
            for msg in reversed(chat_history): # Show most recent first
                context_str += f"{msg.username}: {msg.message}\n"
        else:
            context_str += "- No recent messages.\n"

        # 3. Call the real Gemini API
        gemini = get_gemini_client()
        model = gemini.GenerativeModel('gemini-1.5-flash-latest')
        full_prompt = f"You are a helpful project assistant. Based on the following context, answer the user's question.\n\n--- Context ---\n{context_str}\n--- User Question ---\n{prompt}"
        response = await model.generate_content_async(full_prompt, request_options={"timeout": 60})
        llm_response_text = response.text
    except Exception as e:
        logs.define_logger(logging.ERROR, message=f"Error calling Gemini API: {e}")
        llm_response_text = "Sorry, I encountered an error while processing your request."

    # 4. Save the LLM's response to the chat history.
    # We use a placeholder ID for the bot. This call will bypass the membership check.
    gemini_user_id = "gemini-bot-id"
    gemini_response_message = await chat_service.create_chat_message(
        project_id=project_id,
        user_id=gemini_user_id,
        username="Gemini",
        data=ChatMessageCreate(message=llm_response_text),
        skip_membership_check=True  # Bypass the permission check for the bot.
    )

    # 5. Broadcast the LLM's response directly using the connection manager.
    await chat_manager.broadcast(project_id, {"event": "new_message", "data": gemini_response_message.model_dump(mode="json")})