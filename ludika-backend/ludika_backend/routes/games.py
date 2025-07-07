from fastapi import APIRouter, HTTPException, Depends

from ludika_backend.models.games import Game, GamePublic, GameCreate, GameTag, Tag
from ludika_backend.util.db import get_session
from sqlmodel import Session, select

game_router = APIRouter()


@game_router.get("/", response_model=list[GamePublic])
async def get_games(
    page: int = 0, limit: int = 50, db_session: Session = Depends(get_session), tag_id: int | None = None
):
    """
    Retrieve a list of all games with pagination.
    """
    if tag_id is None:
        statement = select(Game).offset(page * limit).limit(limit)
    else:
        statement = select(Game).join(GameTag).join(Tag).where(Tag.id == tag_id).offset(page * limit).limit(limit)

    results = db_session.exec(statement)
    games = results.all()
    if not games:
        raise HTTPException(status_code=404, detail="No games found")
    return games


@game_router.get(
    "/{game_id}",
    response_model=GamePublic,
)
async def get_game(game_id: int, db_session: Session = Depends(get_session)):
    """
    Retrieve a game by its ID.
    """
    statement = select(Game).where(Game.id == game_id)
    results = db_session.exec(statement)
    game = results.first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@game_router.post("/", response_model=GamePublic)
async def create_game(game: GameCreate, db_session: Session = Depends(get_session)):
    """
    Create a new game.
    """
    db_game = Game.model_validate(game)
    db_session.add(db_game)
    db_session.commit()
    db_session.refresh(db_game)
    return GamePublic.model_validate(db_game)
