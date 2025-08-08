from datetime import datetime, timezone
from typing import Optional, Callable
from uuid import UUID

import requests
from bs4 import BeautifulSoup
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_tavily import TavilySearch

from langchain_core.tools import tool
from sqlmodel import select

from ludika_backend.controllers.image_ops import add_game_image_last
from ludika_backend.controllers.scraping.web_images import get_first_image_from_query

from ludika_backend.models import GamePublic, Game, Tag
from ludika_backend.models.games import GameCreate, GameStatus
from ludika_backend.utils.config import get_config_value
from ludika_backend.utils.db import db_context
from ludika_backend.utils.logs import get_logger

import os

AI_USER_ID = UUID(get_config_value("GenerativeAI", "ai_user_id"))

if os.getenv("TAVILY_API_KEY") is None:
    if get_config_value("GenerativeAI", "tavily_api_key") is None:
        raise ValueError("TAVILY_API_KEY is not set and tavily_api_key is not set in config.ini")
    os.environ["TAVILY_API_KEY"] = get_config_value("GenerativeAI", "tavily_api_key")

wikipedia_api_wrapper = WikipediaAPIWrapper()

tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
    include_answer=False,
)


@tool(description="Search Wikipedia for information about a topic")
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for information about a topic.
    Returns the content of the most relevant Wikipedia article, or a message if no results are found.
    """
    print(f"Searching Wikipedia for: {query}")
    try:
        # Use the Wikipedia API wrapper to search
        result = wikipedia_api_wrapper.run(query)
        if result and result.strip():
            return result
        else:
            return (
                f"No Wikipedia articles found for '{query}'. Try using a different search term or check the spelling."
            )
    except Exception as e:
        get_logger().warning(f"Wikipedia search failed for query '{query}': {str(e)}")
        return f"Unable to search Wikipedia for '{query}'. Error: {str(e)}"


@tool(description="Get the list of current games in the database")
def get_games(name: Optional[str] = None) -> list[GamePublic]:
    print(f"Getting games with name: {name}")
    with db_context() as session:
        statement = select(Game)
        if name:
            statement = statement.where(Game.name.ilike(f"%{name}%"))
        games = session.exec(statement).all()
        return [GamePublic.model_validate(game) for game in games]


@tool(description="Get the list of current tags in the database")
def get_tags() -> list[Tag]:
    print("Getting tags")
    with db_context() as session:
        tags = session.exec(select(Tag)).all()
        return list(tags)


@tool(description="Fetch and parse the content of a web page")
def fetch_page_content(url: str) -> str:
    """
    Fetch the HTML content of a web page and extract useful text information.
    Returns a cleaned text representation of the page content.
    """
    print(f"Fetching page content from: {url}")
    try:
        headers = {
            # this should be good enough
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        # text length limit
        if len(text) > 5000:
            text = text[:5000] + "... (content truncated)"

        return text
    except requests.RequestException as e:
        return f"Error fetching page: {str(e)}"
    except Exception as e:
        return f"Error parsing page: {str(e)}"


def create_game_with_fixed_url(fixed_url: str, game_added_callback: Callable | None = None):
    """Factory function that creates a create_game tool with a fixed URL"""

    @tool(
        description="Create a new game in the database with the predetermined URL",
        return_direct=True,
    )
    def create_game_fixed(name: str, description: str, tags: Optional[list[int]] = None) -> dict:
        print(f"Creating game: {name}, {description}, {fixed_url}, tags: {tags}")
        try:
            with db_context() as session:
                if tags:
                    tag_objects = session.exec(select(Tag).where(Tag.id.in_(tags))).all()
                else:
                    tag_objects = []

                game_data = GameCreate(name=name, description=description, url=fixed_url, tags=tags or [])

                db_game = Game.model_validate(
                    game_data,
                    update={
                        "tags": tag_objects,
                        "proposing_user": AI_USER_ID,
                        "status": GameStatus.APPROVED.value,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    },
                )
                session.add(db_game)
                session.commit()
                session.refresh(db_game)

                try:
                    new_image = get_first_image_from_query(db_game.name + " game")
                    if new_image:
                        new_img_id = add_game_image_last(session, db_game.id, new_image)
                        get_logger().info(f"Successfully added image {new_img_id} to game {db_game.id}")
                except Exception as e:
                    get_logger().warning(f"Failed to add image to game {db_game.id}: {str(e)}")

                if game_added_callback:
                    game_added_callback()
                return {
                    "success": True,
                    "game_id": str(db_game.id),
                    "message": f"Successfully created game '{name}' with ID {db_game.id}",
                    "game": GamePublic.model_validate(db_game),
                }
        except Exception as e:
            return {
                "success": False,
                "game_id": None,
                "message": f"Failed to create game: {str(e)}",
                "game": None,
            }

    return create_game_fixed


def generate_game_object_with_fixed_url(fixed_url: str):
    """Factory function that creates a generate_game_object tool with a fixed URL"""

    @tool(
        description="Generate a GameCreate object without saving to database",
        return_direct=True,
    )
    def generate_game_object_fixed(name: str, description: str, tags: Optional[list[int]] = None) -> dict:
        """
        Generate a GameCreate object with the provided information without saving it to the database.
        This is useful for creating game data structures that can be returned or processed further.
        """
        print(f"Generating GameCreate object: {name}, {description}, {fixed_url}, tags: {tags}")
        game_object = GameCreate(name=name, description=description, url=fixed_url, tags=tags or [])
        return {
            "success": True,
            "game_id": None,
            "message": f"Successfully generated game object for '{name}'",
            "game_object": game_object,
        }

    return generate_game_object_fixed


@tool(
    description="Report that the requested game already exists in the database",
    return_direct=True,
)
def game_exists() -> dict:
    return {
        "success": False,
        "game_id": None,
        "message": "Game already exists in the database",
        "game": None,
    }


def get_tools_for_game_create(url: str, game_added_callback: Callable | None = None):
    """Get tools for game creation with a fixed URL"""
    create_game_tool = create_game_with_fixed_url(url, game_added_callback)
    return [
        get_games,
        get_tags,
        create_game_tool,
        fetch_page_content,
        wikipedia_search,
        tavily_search_tool,
        game_exists,
    ]


def get_tools_for_object_generation(url: str):
    """Get tools for object generation with a fixed URL"""
    generate_game_object_tool = generate_game_object_with_fixed_url(url)
    return [
        get_games,
        get_tags,
        generate_game_object_tool,
        fetch_page_content,
        wikipedia_search,
        tavily_search_tool,
    ]
