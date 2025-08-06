from fastapi import APIRouter

from ludika_backend.controllers.ai import agent_executor_for_game_create, agent_executor_for_object_generation

ai_router = APIRouter()


@ai_router.post("/add-game-from-url")
async def create_game_from_url(url: str):
    return agent_executor_for_game_create.invoke({"url": url})


@ai_router.post("/generate-game-from-url")
async def generate_game_object_from_url(url: str):
    """
    Generate a GameCreate object from a URL without saving it to the database.
    This endpoint uses AI to analyze the web page and create a structured game object.
    """
    return agent_executor_for_object_generation.invoke({"url": url})
