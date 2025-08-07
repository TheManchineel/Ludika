from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ludika_backend.controllers.ai.prompts import get_prompt_for_game_create, get_prompt_for_object_generation
from ludika_backend.controllers.ai.tools import (
    get_tools_for_game_create,
    get_tools_for_object_generation,
    reddit_loader,
)
from ludika_backend.models.games import GameCreate, GamePublic
from ludika_backend.utils.config import get_config_value
from ludika_backend.utils.logs import get_logger
import os

from pydantic.functional_validators import field_validator


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


def create_educational_game_detection_agent():
    """Create an agent that detects educational games in Reddit posts"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an AI assistant that analyzes Reddit posts to detect educational games.


Your task is to:
1. Read the Reddit post content
2. Determine if the post contains or references an educational game
3. If an educational game is found, extract its URL (must start with http:// or https://)
4. If no educational game is found, return 'null'

Educational games include:
- Games designed for learning (math, science, language, etc.)
- Educational apps and platforms
- Learning games for children or adults
- Games used in educational settings

Return ONLY the URL if found, or 'null' if no educational game is referenced.""",
            ),
            ("human", "Analyze this Reddit post for educational games: {post_content}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, [], prompt)
    return AgentExecutor(agent=agent, tools=[], verbose=True)


def validate_url_output(output: str) -> Optional[str]:
    """Validate and parse the URL output from the educational game detection agent"""
    if output is None or output.strip().lower() == "null":
        return None

    url = output.strip()
    if url.startswith(("http://", "https://")):
        return url
    return None


def create_reddit_processing_chain(batch_size: int = 10):
    """Create a chain that processes Reddit posts to find educational games and generate game objects

    Args:
        batch_size: Number of posts to process in parallel per batch (default: 10)
    """

    # Create the educational game detection agent
    detection_agent = create_educational_game_detection_agent(post)

    # Load Reddit posts
    def load_reddit_posts():
        """Load Reddit posts using the reddit_loader"""
        try:
            posts = reddit_loader.load()
            return [post.page_content for post in posts]
        except Exception as e:
            get_logger().error(f"Error loading Reddit posts: {e}")
            return []

    def detect_educational_games_parallel(posts: List[str]) -> List[Optional[str]]:
        """Process posts in parallel to detect educational games and return URLs"""
        if not posts:
            return []

        urls = []

        for i in range(0, len(posts), batch_size):
            batch = posts[i : i + batch_size]
            get_logger().info(
                f"Processing batch {i//batch_size + 1}/{(len(posts) + batch_size - 1)//batch_size} ({len(batch)} posts)"
            )

            detection_agents = {f"post_{j}": detection_agent for j in range(len(batch))}
            inputs = {f"post_{j}": {"post_content": post} for j, post in enumerate(batch)}
            parallel_detector = RunnableParallel(detection_agents)

            try:
                # Execute all detections in parallel for this batch
                results = parallel_detector.invoke(inputs)

                # Extract URLs from results
                batch_urls = []
                for j in range(len(batch)):
                    result_key = f"post_{j}"
                    if result_key in results:
                        result = results[result_key]
                        url = validate_url_output(result.get("output", ""))
                        batch_urls.append(url)
                    else:
                        batch_urls.append(None)

                urls.extend(batch_urls)

            except Exception as e:
                get_logger().warning(f"Error in parallel detection for batch {i//batch_size + 1}: {e}")
        return urls

    # Filter out None URLs and create game generation executors
    def create_game_generators(urls: List[Optional[str]]) -> List[AgentExecutor]:
        """Create agent executors for game generation from valid URLs"""
        valid_urls = [url for url in urls if url is not None]
        return [create_agent_executor_for_object_generation(url) for url in valid_urls]

    # Execute all game generators in parallel
    def generate_games(executors: List[AgentExecutor]) -> List[dict]:
        """Execute all game generation agents in parallel"""
        if not executors:
            return []

        # Create a parallel runnable
        parallel_executor = RunnableParallel({f"game_{i}": executor for i, executor in enumerate(executors)})

        try:
            results = parallel_executor.invoke({})
            return list(results.values())
        except Exception as e:
            get_logger().error(f"Error executing game generators: {e}")
            return []

    # Create the complete chain with parallel detection
    chain = (
        RunnablePassthrough.assign(posts=load_reddit_posts)
        .assign(urls=lambda x: detect_educational_games_parallel(x["posts"]))
        .assign(executors=lambda x: create_game_generators(x["urls"]))
        .assign(games=lambda x: generate_games(x["executors"]))
    )

    return chain


def run_reddit_processing_chain(batch_size: int = 10):
    """Run the complete Reddit processing chain

    Args:
        batch_size: Number of posts to process in parallel per batch (default: 10)
    """
    chain = create_reddit_processing_chain(batch_size)
    result = chain.invoke({})

    get_logger().info(f"Processed {len(result.get('posts', []))} Reddit posts")
    get_logger().info(f"Found {len([url for url in result.get('urls', []) if url is not None])} educational games")
    get_logger().info(f"Generated {len(result.get('games', []))} game objects")

    return result
