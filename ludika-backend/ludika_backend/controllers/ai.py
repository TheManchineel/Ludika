from typing import Optional
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from google.ai.generativelanguage_v1beta.types import Tool as GenAITool

from ludika_backend.controllers.image_ops import add_game_image_last
from ludika_backend.controllers.image_web_scraping import get_image_links, get_first_image_from_query
from ludika_backend.models.games import Game, GameCreate, GamePublic, GameStatus, Tag
from ludika_backend.utils.config import get_config_value
from uuid import UUID
from datetime import datetime, timezone
import os
import requests
from bs4 import BeautifulSoup

from ludika_backend.utils.db import db_context
from sqlmodel import select

from ludika_backend.utils.logs import get_logger

if os.getenv("GOOGLE_API_KEY") is None:
    if get_config_value("GenerativeAI", "gemini_api_key") is None:
        raise ValueError("GOOGLE_API_KEY is not set and gemini_api_key is not set in config.ini")
    os.environ["GOOGLE_API_KEY"] = get_config_value("GenerativeAI", "gemini_api_key")

MODEL_NAME = get_config_value("GenerativeAI", "model")
AI_USER_ID = UUID(get_config_value("GenerativeAI", "ai_user_id"))


llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.1)
tooled_llm = llm.bind_tools([GenAITool(google_search={})])
wikipedia_api_wrapper = WikipediaAPIWrapper()
wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_api_wrapper)


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


@tool(description="Create a new game in the database")
def create_game(name: str, description: str, url: str, tags: Optional[list[int]] = None) -> GamePublic:
    print(f"Creating game: {name}, {description}, {url}, tags: {tags}")
    with db_context() as session:
        if tags:
            tag_objects = session.exec(select(Tag).where(Tag.id.in_(tags))).all()
        else:
            tag_objects = []

        game_data = GameCreate(name=name, description=description, url=url, tags=tags or [])

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

        # let's try to add an image
        new_image = get_first_image_from_query(url)
        if new_image:
            new_img_id = add_game_image_last(session, db_game.id, new_image)
            get_logger().info(f"Successfully added image {new_img_id} to game {db_game.id}")

        return GamePublic.model_validate(db_game)


@tool(description="Generate a GameCreate object without saving to database")
def generate_game_object(name: str, description: str, url: str, tags: Optional[list[int]] = None) -> GameCreate:
    """
    Generate a GameCreate object with the provided information without saving it to the database.
    This is useful for creating game data structures that can be returned or processed further.
    """
    print(f"Generating GameCreate object: {name}, {description}, {url}, tags: {tags}")
    return GameCreate(name=name, description=description, url=url, tags=tags or [])


tools_for_game_create = [get_games, get_tags, create_game, fetch_page_content, wikipedia_tool]
tools_for_object_generation = [get_games, get_tags, generate_game_object, fetch_page_content, wikipedia_tool]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI assistant that can interact with a game database.
     You have access to tools to:
     - Get games from the database
     - Get tags from the database
     - Create new games in the database
     - Search Wikipedia for information
     - Search Google for information

     When creating games, make sure to:
     1. First get the available tags
     2. Use `wikipedia` and `google_search` to find information about the game
     3. Choose appropriate tag IDs from the available tags
     4. Create the game with valid data

     Always use the tools when asked to perform database operations.""",
        ),
        (
            "human",
            """Create a new game in the database with the following requirements:
        1. First, determine the name of the game based on this URL: {url}. You can also use the `google_search` and `wikipedia` tools to find more information.
        2. Check if the game already exists in the database with the `get_games` tool. If it does, return early and do not create a new game.
        3. If the game does not exist, use the `get_tags` tool to get a complete list of tags.
        4. Use `google_search` and `wikipedia` to find more information about the game and choose all the appropriate tags that apply, if you don't have enough information, return early and do not create a new game.
        5. If the game does not already exist in the database and you have enough information, use `create_game` to create a new game with the following requirements:
           - name: the name of the game
           - description: a short, concise description of the game (use `google_search` and `wikipedia` for more accurate info)
           - url: {url}
           - tags: a list of tag IDs, which you selected in step 4""",
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

prompt_for_object_generation = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI assistant that can analyze web pages and generate game data objects.
     You have access to tools to:
     - Get games from the database
     - Get tags from the database
     - Fetch and parse web page content
     - Generate GameCreate objects (without saving to database)
     - Search Wikipedia for information
     - Search Google for information

     When generating a GameCreate object, make sure to:
     1. First get the available tags
     2. Use `fetch_page_content` to get detailed information about the game from the provided URL
     3. Use `wikipedia` and `google_search` to find additional information about the game
     4. Choose appropriate tag IDs from the available tags
     5. Generate a GameCreate object with valid data

     Always use the tools when asked to perform operations.""",
        ),
        (
            "human",
            """Generate a GameCreate object based on this URL: {url}. Follow these steps:
        1. First, use `fetch_page_content` to get information directly from the URL.
        2. Determine the name of the game from the page content. You can also use `google_search` and `wikipedia` tools to find more information.
        3. Check if the game already exists in the database with the `get_games` tool. If it does, still continue to generate the object.
        4. Use the `get_tags` tool to get a complete list of available tags.
        5. Use `google_search` and `wikipedia` to find more information about the game and choose all the appropriate tags that apply.
        6. Use `generate_game_object` to create a GameCreate object with the following requirements:
           - name: the name of the game
           - description: a comprehensive description of the game (use information from the web page, `google_search` and `wikipedia`)
           - url: {url}
           - tags: a list of tag IDs that you selected in step 5

        Return the GameCreate object directly without saving it to the database.""",
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent_for_game_create = create_tool_calling_agent(tooled_llm, tools_for_game_create, prompt)
agent_for_object_generation = create_tool_calling_agent(
    tooled_llm, tools_for_object_generation, prompt_for_object_generation
)

agent_executor_for_game_create = AgentExecutor(agent=agent_for_game_create, tools=tools_for_game_create, verbose=True)
agent_executor_for_object_generation = AgentExecutor(
    agent=agent_for_object_generation, tools=tools_for_object_generation, verbose=True
)
