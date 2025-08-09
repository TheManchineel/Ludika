from typing import Optional, Callable
from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.rate_limiters import InMemoryRateLimiter

from ludika_backend.controllers.ai.prompts import (
    GAME_DETECTION_PROMPT,
    get_prompt_for_game_create,
    get_prompt_for_object_generation,
)
from ludika_backend.controllers.ai.tools import (
    get_tools_for_game_create,
    get_tools_for_object_generation,
    tavily_search_tool,
)
from ludika_backend.models.games import GameCreate, GamePublic
from ludika_backend.utils.config import get_config_value
from ludika_backend.utils.logs import get_logger
import os

from pydantic.functional_validators import field_validator


rate_limiter_nvidia = InMemoryRateLimiter(
    requests_per_second=1.0,
    check_every_n_seconds=0.1,
    max_bucket_size=15,
)


class GameCreationResponse(BaseModel):
    """Structured response for game creation operations"""

    success: bool = Field(description="Whether the operation was successful")
    game_id: Optional[str] = Field(
        description="UUID of the created game, or null if not created"
    )
    message: Optional[str] = Field(
        description="Human-readable message about the operation"
    )
    game: Optional[GamePublic] = Field(
        description="The created game object, if successful"
    )


class GameObjectGenerationResponse(BaseModel):
    """Structured response for game object generation operations"""

    success: bool = Field(description="Whether the operation was successful")
    game_id: Optional[str] = Field(description="Always null for generation operations")
    message: Optional[str] = Field(
        description="Human-readable message about the operation"
    )
    game_object: Optional[GameCreate] = Field(
        description="The generated game object, if successful"
    )


class EducationalGameURLResponse(BaseModel):
    """Structured response for educational game URL detection"""

    url: Optional[str] = Field(
        description="URL of the educational game if found, otherwise null",
    )

    @field_validator("url")
    def must_be_url(cls, v):
        if v is not None:
            if not v.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")
        return v


if os.getenv("NVIDIA_API_KEY") is None:
    if get_config_value("GenerativeAI", "nvidia_api_key") is None:
        raise ValueError(
            "NVIDIA_API_KEY is not set and nvidia_api_key is not set in config.ini"
        )
    os.environ["NVIDIA_API_KEY"] = get_config_value("GenerativeAI", "nvidia_api_key")

NVIDIA_MODEL_NAME = get_config_value("GenerativeAI", "nvidia_model")

llm = ChatNVIDIA(
    model=NVIDIA_MODEL_NAME,
    rate_limiter=(
        rate_limiter_nvidia
        if bool(get_config_value("GenerativeAI", "rate_limit_nvidia"))
        else None
    ),
)


def create_agent_executor_for_game_create(
    url: str, game_added_callback: Callable | None = None
):
    """Create an agent executor for game creation with a fixed URL"""
    tools = get_tools_for_game_create(url, game_added_callback)
    prompt = get_prompt_for_game_create(url)

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def create_agent_executor_for_object_generation(url: str):
    """Create an agent executor for object generation with a fixed URL"""
    tools = get_tools_for_object_generation(url)
    prompt = get_prompt_for_object_generation(url)

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


class PossibleGameURLOutput(BaseModel):
    url: str | None = Field(
        description="The URL of the possible game, or None if no game is found"
    )

    @field_validator("url")
    def validate_url(cls, v):
        if not v.startswith("https://") or not v.startswith("http://"):
            get_logger().warning(f"Invalid URL: {v}, skipping")
            return None
        return v


game_detection_agent = create_tool_calling_agent(
    llm,
    [tavily_search_tool],
    prompt=ChatPromptTemplate.from_messages(
        [
            ("system", GAME_DETECTION_PROMPT),
            ("human", "The post is:\n\n{post_content}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    ),
)

game_detection_executor = AgentExecutor(
    agent=game_detection_agent, tools=[tavily_search_tool]
)


class DetectionResult(BaseModel):
    has_game_url: bool
    url: Optional[str]
