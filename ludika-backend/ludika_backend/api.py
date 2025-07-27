import subprocess
from fastapi import FastAPI
from datetime import datetime

from fastapi.staticfiles import StaticFiles

# Import models module to trigger model rebuilding
from ludika_backend.routes.auth import auth_router
from ludika_backend.routes.games import game_router
from ludika_backend.routes.review import review_router
from ludika_backend.routes.tags import tag_router
from ludika_backend.routes.users import user_router

app = FastAPI()


@app.get("/status")
@app.get("/")
async def status():
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


app.include_router(game_router, prefix="/games")
app.include_router(tag_router, prefix="/tags")
app.include_router(user_router, prefix="/users")
app.include_router(review_router, prefix="/reviews")

app.include_router(auth_router, prefix="/auth")

app.mount("/static", StaticFiles(directory="./static"), name="static")
