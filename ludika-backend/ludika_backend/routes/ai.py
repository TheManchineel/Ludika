from fastapi import APIRouter, Depends, HTTPException

from ludika_backend.controllers.ai.agents import (
    create_agent_executor_for_game_create,
    create_agent_executor_for_object_generation,
)
from ludika_backend.controllers.auth import get_current_user
from ludika_backend.models import User

ai_router = APIRouter()


@ai_router.post("/add-game-from-url")
async def create_game_from_url(url: str, current_user: User = Depends(get_current_user)):
    """Create and immediately approve a new game given a valid URL, with the power of AI!"""

    if current_user.can_use_ai():
        agent_executor = create_agent_executor_for_game_create(url)
        result = agent_executor.invoke({})
        return result
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to use AI features.")


@ai_router.post("/generate-game-from-url")
async def generate_game_object_from_url(url: str, current_user: User = Depends(get_current_user)):
    """Generate a GameCreate object from a URL without saving it to the database. This endpoint uses AI to analyze the web page and create a structured game object."""

    if current_user.can_use_ai():
        agent_executor = create_agent_executor_for_object_generation(url)
        result = agent_executor.invoke({})
        return result
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to use AI features.")
