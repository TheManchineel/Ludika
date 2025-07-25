import logging


def get_logger() -> logging.Logger:
    """
    Returns a logger for the application.
    """

    return logging.getLogger("uvicorn.error")
