import subprocess
from fastapi import FastAPI
from sys import version as python_version
from datetime import datetime

from fastapi.staticfiles import StaticFiles

# Import models module to trigger model rebuilding
from ludika_backend.routes.ai import ai_router
from ludika_backend.routes.auth import auth_router
from ludika_backend.routes.games import game_router
from ludika_backend.routes.review import review_router
from ludika_backend.routes.tags import tag_router
from ludika_backend.routes.users import user_router

app = FastAPI(
    title="Ludika API",
    description="API for the Ludika platform",
    version="0.1.0",
)

initialization_time = datetime.now()


@app.get("/status")
@app.get("/")
async def status():
    """
    Root endpoint that returns status information.
    """

    start = datetime.now()

    data = {
        "status": "up",
        "uptime": str(datetime.now() - initialization_time),
        "server_time": datetime.now().isoformat(),
        "python_version": python_version,
        "time_taken": f"{int((datetime.now() - start).microseconds / 1000)} ms",
    }
    return data


app.include_router(game_router, prefix="/games")
app.include_router(tag_router, prefix="/tags")
app.include_router(user_router, prefix="/users")
app.include_router(review_router, prefix="/reviews")
app.include_router(auth_router, prefix="/auth")
app.include_router(ai_router, prefix="/ai")  # we live in 2077

app.mount("/static", StaticFiles(directory="./static"), name="static")
