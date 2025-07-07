import subprocess
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime

from ludika_backend.routes.games import game_router
from ludika_backend.util.config import get_config_value

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=get_config_value("GoogleAuth", "secret_key"))


@app.get("/")
async def root():
    """
    Root endpoint that returns status information.
    """

    start = datetime.now()

    data = {
        "status": "up",
        "uptime": subprocess.check_output(["uptime"]).decode("utf-8").strip(),
        "server_time": datetime.now().isoformat(),
        "python_version": subprocess.check_output(["python3", "--version"]).decode("utf-8").strip(),
        "uvicorn_version": subprocess.check_output(["uvicorn", "--version"]).decode("utf-8").strip(),
        "system": subprocess.check_output(["uname", "-a"]).decode("utf-8").strip(),
        "time_taken": f"{int((datetime.now() - start).microseconds / 1000)} ms",
    }

    return data


@app.get("/health")
async def health_check():
    """
    Health check endpoint that returns a status message.
    """
    return {"status": "ok"}


app.include_router(game_router, prefix="/games")
