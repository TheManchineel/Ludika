from datetime import timezone, datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Security
from fastapi import UploadFile, File, Response
import os

from ludika_backend.controllers.auth import get_current_user, get_current_user_optional
from ludika_backend.models.games import (
    Game,
    GamePublic,
    GameWithReviews,
    GameCreate,
    Tag,
    GameUpdate,
    GameImage,
    GameStatus,
)
from ludika_backend.models.users import User

from ludika_backend.utils.db import get_session
from sqlmodel import Session, select, or_
from ludika_backend.utils.image_ops import (
    add_game_image_last,
    overwrite_game_image,
    delete_image_from_game,
    delete_all_game_images,
)

game_router = APIRouter()

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "static")


@game_router.get("/")
async def get_games(
    page: int = 0,
    limit: int = 50,
    search: str | None = None,
    tags: str | None = None,
    db_session: Session = Depends(get_session),
) -> list[GamePublic]:
    """Retrieve a list of all approved games with pagination, tag filtering and search."""

    statement = (
        select(Game)
        .where(or_(Game.status == GameStatus.APPROVED.value)))

    if tags:
        try:
            tag_ids = [int(tag.strip()) for tag in tags.split(",")]
            statement = statement.where(Game.tags.any(Tag.id.in_(tag_ids)))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tags format (must be a comma-separated list of integers)")


    if search:
        statement = statement.where(or_(Game.name.ilike(f"%{search}%"), Game.description.ilike(f"%{search}%"), Game.tags.any(Tag.name.ilike(f"%{search}%"))))

    statement = statement.offset(page * limit).limit(limit)


    results = db_session.exec(statement)
    games = results.all()
    return games


@game_router.get("/my-games")
async def get_my_games(
    page: int = 0,
    limit: int = 50,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> list[GamePublic]:
    """Get games created by the current user."""
    statement = (
        select(Game)
        .where(Game.proposing_user == current_user.uuid)
        .offset(page * limit)
        .limit(limit)
    )
    results = db_session.exec(statement)
    games = results.all()
    return games


@game_router.get("/waiting-for-approval")
async def get_games_waiting_for_approval(
    page: int = 0,
    limit: int = 50,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> list[GamePublic]:
    """Get games waiting for approval (privileged users only)."""
    if not current_user.is_privileged():
        raise HTTPException(
            status_code=403, detail="You do not have permission to view this."
        )

    statement = (
        select(Game)
        .where(Game.status == GameStatus.SUBMITTED.value)
        .offset(page * limit)
        .limit(limit)
    )
    results = db_session.exec(statement)
    games = results.all()
    return games


@game_router.get("/{game_id}")
async def get_game(
    game_id: int,
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
) -> GamePublic:
    """Retrieve a game by its ID."""
    statement = select(Game).where(Game.id == game_id)
    if current_user:
        if not current_user.is_privileged:
            statement = statement.where(
                or_(
                    Game.proposing_user == current_user.uuid,
                    Game.status == GameStatus.APPROVED.value,
                )
            )
    else:
        statement = statement.where(Game.status == GameStatus.APPROVED.value)
    results = db_session.exec(statement)
    game = results.first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@game_router.get("/{game_id}/with-reviews")
async def get_game_with_reviews(
    game_id: int,
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
) -> GameWithReviews:
    """Retrieve a game by its ID with reviews included."""
    statement = select(Game).where(Game.id == game_id)
    if current_user:
        if not current_user.is_privileged:
            statement = statement.where(
                or_(
                    Game.proposing_user == current_user.uuid,
                    Game.status == GameStatus.APPROVED.value,
                )
            )
    else:
        statement = statement.where(Game.status == GameStatus.APPROVED.value)
    results = db_session.exec(statement)
    game = results.first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game





@game_router.post("/")
async def create_game(
    game: GameCreate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> GamePublic:
    """Create a new game."""
    tags = db_session.exec(select(Tag).where(Tag.id.in_(game.tags))).all()
    db_game = Game.model_validate(
        game,
        update={
            "proposing_user": current_user.uuid,
            "tags": tags,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "status": "draft",
        },
    )
    db_session.add(db_game)
    db_session.commit()
    db_session.refresh(db_game)
    return GamePublic.model_validate(db_game)


@game_router.delete("/{game_id}")
async def delete_game(
    game_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """Delete a game (only by creator or privileged users)."""
    game = db_session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if current_user.can_edit_game(game):
        delete_all_game_images(db_session, game_id)
        db_session.delete(game)
        db_session.commit()
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this game."
        )


@game_router.patch("/{game_id}")
async def update_game(
    game_id: int,
    game_update: GameUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
) -> GamePublic:
    """Update a game (only by creator or privileged users)."""
    db_game = db_session.get(Game, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not current_user.can_edit_game(db_game):
        raise HTTPException(
            status_code=403, detail="You do not have permission to update this game."
        )
    update_data = game_update.model_dump(exclude_unset=True)

    if "status" in update_data:
        if not current_user.is_privileged():
            if (
                update_data["status"] != GameStatus.SUBMITTED.value
                or db_game.status != GameStatus.DRAFT.value
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to update the status of this game.",
                )
        if update_data["status"] == GameStatus.APPROVED.value:
            db_game.approved_by = current_user.uuid
            db_game.status = GameStatus.APPROVED.value

    # Handle tags separately
    if "tags" in update_data:
        tag_ids = update_data.pop("tags")
        if tag_ids is not None:
            tags = db_session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all()
            db_game.tags = tags
    db_game.sqlmodel_update(update_data)
    db_game.updated_at = datetime.now(timezone.utc)
    db_session.commit()
    db_session.refresh(db_game)
    return GamePublic.model_validate(db_game)


@game_router.get("/{game_id}/images/{image_no}")
async def get_game_image(
    game_id: int,
    image_no: int,
    db_session: Session = Depends(get_session),
    current_user: User | None = Security(get_current_user_optional),
):
    """Get a specific image for a game."""
    game = db_session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not game.is_visible_by(current_user):
        raise HTTPException(
            status_code=403, detail="You do not have permission to view this game."
        )
    image_record = db_session.exec(
        select(GameImage).where(
            GameImage.game_id == game_id, GameImage.position == image_no
        )
    ).first()
    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")
    file_path = os.path.join(STATIC_DIR, image_record.image)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return Response(content=open(file_path, "rb").read(), media_type="image/webp")


@game_router.post("/{game_id}/images", status_code=201)
async def post_game_image(
    game_id: int,
    file: UploadFile = File(...),
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """Upload a new image for a game."""
    game = db_session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not current_user.can_edit_game(game):
        raise HTTPException(
            status_code=403, detail="You do not have permission to edit this game."
        )
    img_uuid = add_game_image_last(db_session, game_id, file.file)
    return {"status": "ok", "filename": img_uuid}


@game_router.put("/{game_id}/images/{image_no}")
async def replace_game_image(
    game_id: int,
    image_no: int,
    file: UploadFile = File(...),
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """Replace an existing image for a game."""
    game = db_session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not current_user.can_edit_game(game):
        raise HTTPException(
            status_code=403, detail="You do not have permission to edit this game."
        )
    img_uuid = overwrite_game_image(db_session, game_id, image_no, file.file)
    if not img_uuid:
        raise HTTPException(status_code=404, detail="Image not found to replace")
    return {"status": "ok", "filename": img_uuid}


@game_router.delete("/{game_id}/images/{image_no}")
async def delete_game_image(
    game_id: int,
    image_no: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    """Delete a specific image from a game."""
    game = db_session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not current_user.can_edit_game(game):
        raise HTTPException(
            status_code=403, detail="You do not have permission to edit this game."
        )
    deleted = delete_image_from_game(db_session, game_id, image_no)
    if not deleted:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"status": "ok", "deleted": True}
