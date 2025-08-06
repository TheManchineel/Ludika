from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_prompt_for_game_create(url: str):
    """Get prompt template for game creation with the URL embedded"""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an AI assistant that can interact with a game database.
You have access to tools to:
- Get games from the database
- Get tags from the database
- Create new games in the database (with a predetermined URL)
- Search Wikipedia for information
- Search the web using Tavily for information
- Search Google for information

When creating games, make sure to:
1. First get the available tags
2. Use `wikipedia_search`, `tavily_search_tool`, and `google_search` to find information about the game
3. Choose appropriate tag IDs from the available tags
4. Create the game with valid data

Always use the tools when asked to perform database operations.""",
            ),
            (
                "human",
                f"""Create a new game in the database for URL: {url}
1. First, determine the name of the game based on this URL: {url}. You can also use the `tavily_search_tool`, `google_search` and `wikipedia_search` tools to find more information.
2. Check if the game already exists in the database with the `get_games` tool. If it does, stop and do not create a new game, but call the `game_exists` tool instead.
3. If the game does not exist, use the `get_tags` tool to get a complete list of tags.
4. Use `tavily_search`, `google_search` and `wikipedia_search` to find more information about the game and choose all the appropriate tags that apply. If you don't have enough information, stop and do not create a game.
5. If the game does not already exist in the database and you have enough information, use `create_game_fixed` to create a new game with:
    - name: the name of the game
    - description: a short, concise description of the game (use `tavily_search`, `google_search` and `wikipedia_search` for more accurate info)
    - tags: a list of tag IDs, which you selected in step 4

The URL is already predetermined and will be saved automatically. The create_game_fixed tool will return the final result directly.""",
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


def get_prompt_for_object_generation(url: str):
    """Get prompt template for object generation with the URL embedded"""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an AI assistant that can analyze web pages and generate game data objects.
You have access to tools to:
- Get games from the database
- Get tags from the database
- Fetch and parse web page content
- Generate GameCreate objects (without saving to database, with predetermined URL)
- Search Wikipedia for information
- Search the web using Tavily for information
- Search Google for information

When generating a GameCreate object, make sure to:
1. First get the available tags
2. Use `fetch_page_content` to get detailed information about the game from the provided URL
3. Use `wikipedia_search`, `tavily_search`, and `google_search` to find additional information about the game
4. Choose appropriate tag IDs from the available tags
5. Generate a GameCreate object with valid data

Always use the tools when asked to perform operations.""",
            ),
            (
                "human",
                f"""Generate a GameCreate object based on this URL: {url}. Follow these steps:
1. First, use `fetch_page_content` to get information directly from the URL.
2. Determine the name of the game from the page content. You can also use `tavily_search_tool`, `google_search` and `wikipedia_search` tools to find more information.
3. Check if the game already exists in the database with the `get_games` tool. If it does, still continue to generate the object.
4. Use the `get_tags` tool to get a complete list of available tags.
5. Use `tavily_search_tool`, `google_search` and/or `wikipedia_search` to find more information about the game and choose all the appropriate tags that apply.
6. Use `generate_game_object_fixed` to create a GameCreate object with:
    - name: the name of the game
    - description: a comprehensive description of the game (use information from the web page, `tavily_search`, `google_search` and `wikipedia_search`)
    - tags: a list of tag IDs that you selected in step 5

The URL is already predetermined and will be saved automatically. The generate_game_object_fixed tool will return the final result directly.""",
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
