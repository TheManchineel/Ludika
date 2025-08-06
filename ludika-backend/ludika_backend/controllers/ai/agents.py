from typing import Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent

from google.ai.generativelanguage_v1beta.types import Tool as GenAITool

from ludika_backend.controllers.ai.prompts import get_prompt_for_game_create, get_prompt_for_object_generation
from ludika_backend.controllers.ai.tools import get_tools_for_game_create, get_tools_for_object_generation
from ludika_backend.models.games import GameCreate, GamePublic
from ludika_backend.utils.config import get_config_value
import os


# Pydantic models for structured responses
class GameCreationResponse(BaseModel):
    """Structured response for game creation operations"""

    success: bool = Field(description="Whether the operation was successful")
    game_id: Optional[str] = Field(description="UUID of the created game, or null if not created")
    message: Optional[str] = Field(description="Human-readable message about the operation")
    game: Optional[GamePublic] = Field(description="The created game object, if successful")


class GameObjectGenerationResponse(BaseModel):
    """Structured response for game object generation operations"""

    success: bool = Field(description="Whether the operation was successful")
    game_id: Optional[str] = Field(description="Always null for generation operations")
    message: Optional[str] = Field(description="Human-readable message about the operation")
    game_object: Optional[GameCreate] = Field(description="The generated game object, if successful")


if os.getenv("GOOGLE_API_KEY") is None:
    if get_config_value("GenerativeAI", "gemini_api_key") is None:
        raise ValueError("GOOGLE_API_KEY is not set and gemini_api_key is not set in config.ini")
    os.environ["GOOGLE_API_KEY"] = get_config_value("GenerativeAI", "gemini_api_key")

MODEL_NAME = get_config_value("GenerativeAI", "model")


llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.1)
tooled_llm = llm.bind_tools([GenAITool(google_search={})])


def create_agent_executor_for_game_create(url: str):
    """Create an agent executor for game creation with a fixed URL"""
    tools = get_tools_for_game_create(url)
    prompt = get_prompt_for_game_create(url)

    # Use the original tooled_llm since we're using return_direct=True in tools
    agent = create_tool_calling_agent(tooled_llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def create_agent_executor_for_object_generation(url: str):
    """Create an agent executor for object generation with a fixed URL"""
    tools = get_tools_for_object_generation(url)
    prompt = get_prompt_for_object_generation(url)

    # Use the original tooled_llm since we're using return_direct=True in tools
    agent = create_tool_calling_agent(tooled_llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
