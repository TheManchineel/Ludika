import os

from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from ludika_backend.utils.config import get_config_value

llm = None
TEMPERATURE_SETTING = 0.0

rate_limiter = (
    (
        InMemoryRateLimiter(
            requests_per_second=1.0,
            check_every_n_seconds=0.1,
            max_bucket_size=15,
        )
        if bool(get_config_value("GenerativeAI", "rate_limit_llm"))
        else None
    ),
)


match get_config_value("GenerativeAI", "ai_main_provider"):
    case "nvidia":
        if os.getenv("NVIDIA_API_KEY") is None:
            if get_config_value("GenerativeAI", "nvidia_api_key") is None:
                raise ValueError(
                    "NVIDIA_API_KEY is not set and nvidia_api_key is not set in config.ini"
                )
            os.environ["NVIDIA_API_KEY"] = get_config_value(
                "GenerativeAI", "nvidia_api_key"
            )
        NVIDIA_MODEL_NAME = get_config_value("GenerativeAI", "nvidia_model")
        llm = ChatNVIDIA(
            model=NVIDIA_MODEL_NAME,
            rate_limiter=(rate_limiter),
            temperature=TEMPERATURE_SETTING,
        )
    case "google":
        if os.getenv("GOOGLE_API_KEY") is None:
            if get_config_value("GenerativeAI", "google_gemini_api_key") is None:
                raise ValueError(
                    "GOOGLE_API_KEY is not set and google_api_key is not set in config.ini"
                )
            os.environ["GOOGLE_API_KEY"] = get_config_value(
                "GenerativeAI", "google_api_key"
            )
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=TEMPERATURE_SETTING,
            rate_limiter=rate_limiter,
        )
    case _:
        raise ValueError("Invalid AI provider specified.")
