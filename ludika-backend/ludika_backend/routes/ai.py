from fastapi import APIRouter, Depends, HTTPException

from ludika_backend.controllers.ai.agents import (
    create_agent_executor_for_game_create,
    create_agent_executor_for_object_generation,
    run_full_reddit_pipeline,
)
from ludika_backend.controllers.auth import get_current_user
from ludika_backend.models import User
from ludika_backend.controllers.reddit_scraping import get_top_posts


ai_router = APIRouter()

# The endpoints in this file are not defined as asynchronous to avoid blocking the main thread because they rely on
# various third-party libraries which are blocking. FastAPI will automatically launch them in a separate thread.


@ai_router.post("/add-game-from-url")
def create_game_from_url(url: str, current_user: User = Depends(get_current_user)):
    """Create and immediately approve a new game given a valid URL, with the power of AI!"""

    if current_user.can_use_ai():
        agent_executor = create_agent_executor_for_game_create(url)
        result = agent_executor.invoke({})
        return result.get("output")
    else:
        raise HTTPException(
            status_code=403, detail="You do not have permission to use AI features."
        )


@ai_router.post("/generate-game-from-url")
def generate_game_object_from_url(
    url: str, current_user: User = Depends(get_current_user)
):
    """Generate a GameCreate object from a URL without saving it to the database. This endpoint uses AI to analyze the web page and create a structured game object."""

    if current_user.can_use_ai():
        agent_executor = create_agent_executor_for_object_generation(url)
        result = agent_executor.invoke({})
        return result.get("output")
    else:
        raise HTTPException(
            status_code=403, detail="You do not have permission to use AI features."
        )


@ai_router.post("/add-games-from-reddit")
def process_reddit_for_educational_games(
    current_user: User = Depends(get_current_user),
):
    """Process Reddit posts to find educational games and generate game objects automatically."""

    if not current_user.can_use_ai():
        raise HTTPException(
            status_code=403, detail="You do not have permission to use AI features."
        )

    try:
        run_full_reddit_pipeline()
        return {
            "success": True,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing Reddit posts: {str(e)}",
        )


@ai_router.get("/test-reddit-fetch")
def test_reddit_loader(current_user: User = Depends(get_current_user)):
    if not current_user.can_use_ai():
        raise HTTPException(
            status_code=403, detail="You do not have permission to use AI features."
        )
    """Test the Reddit loader to fetch posts from specified subreddits."""
    try:
        return get_top_posts()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching Reddit posts: {str(e)}",
        )
