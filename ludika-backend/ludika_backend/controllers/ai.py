from typing import Optional
from fastapi import APIRouter
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
from ludika_backend.models.games import Game, GameCreate, GamePublic, GameStatus, Tag
from ludika_backend.utils.config import get_config_value
from uuid import UUID
from datetime import datetime, timezone
import os

from ludika_backend.utils.db import db_context
from sqlmodel import select

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
            statement = statement.where(Game.name.ilike(f"%{name}%"))  # Fixed: was .title, should be .name
        games = session.exec(statement).all()
        return [GamePublic.model_validate(game) for game in games]


@tool(description="Get the list of current tags in the database")
def get_tags() -> list[Tag]:
    print("Getting tags")
    with db_context() as session:
        tags = session.exec(select(Tag)).all()
        return list(tags)


# TODO: add image search functionality
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
        return GamePublic.model_validate(db_game)


tools = [get_games, get_tags, create_game, wikipedia_tool]

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

agent = create_tool_calling_agent(tooled_llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

ai_test_router = APIRouter()


@ai_test_router.post("/create-game-from-url")
async def create_game_from_url(url: str):
    return agent_executor.invoke({"url": url})
