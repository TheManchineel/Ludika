import subprocess
from fastapi import FastAPI
from datetime import datetime

from fastapi.params import Security
from fastapi.staticfiles import StaticFiles

from ludika_backend.controllers.auth import get_current_user
from ludika_backend.models.users import User, UserPublic
from ludika_backend.routes.auth import auth_router
from ludika_backend.routes.games import game_router
from ludika_backend.routes.review import review_router
from ludika_backend.routes.tags import tag_router
from ludika_backend.routes.users import user_router

app = FastAPI()


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
        "python_version": subprocess.check_output(["python3", "--version"])
        .decode("utf-8")
        .strip(),
        "uvicorn_version": subprocess.check_output(["uvicorn", "--version"])
        .decode("utf-8")
        .strip(),
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


@app.get("/me", response_model=UserPublic)
async def get_me(current_user: User = Security(get_current_user)):
    """
    Get info on the logged-in user.
    """
    return current_user


app.include_router(game_router, prefix="/games")
app.include_router(tag_router, prefix="/tags")
app.include_router(user_router, prefix="/users")
app.include_router(review_router, prefix="/reviews")

app.include_router(auth_router, prefix="/auth")

app.mount("/static", StaticFiles(directory="./static"), name="static")
