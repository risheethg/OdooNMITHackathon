from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth_model import User
from app.models.chat_model import GeminiRequest
from app.services.auth_service import get_current_active_user
from app.services import llm_service, chat_service

router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)

@router.post("/gemini/{project_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_gemini_prompt(
    project_id: str,
    request: GeminiRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Receives a prompt for the Gemini LLM, validates user membership,
    and triggers the asynchronous response generation.
    """
    if not chat_service._is_user_project_member(project_id, current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this project.")

    await llm_service.handle_gemini_prompt(project_id, request.prompt, current_user.user_id, current_user.username)

    return {"status": "processing", "message": "Prompt is being processed."}