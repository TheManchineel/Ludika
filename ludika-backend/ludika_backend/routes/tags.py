from fastapi import Depends, APIRouter, HTTPException
from fastapi.params import Security
from sqlmodel import Session, select

from ludika_backend.controllers.auth import get_current_user
from ludika_backend.models.games import Tag, TagUpdate
from ludika_backend.models.users import UserRole, User
from ludika_backend.utils.db import get_session

tag_router = APIRouter()


@tag_router.get("/")
async def get_tags(db_session: Session = Depends(get_session)):
    """
    Get all tags.
    """
    statement = select(Tag)
    results = db_session.exec(statement)
    tags = results.all()
    return tags


@tag_router.post("/")
async def add_tag(
    name: str,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(
            status_code=403, detail="You do not have permission to create tags."
        )

    if db_session.exec(select(Tag).where(Tag.name == name)).first() is not None:
        raise HTTPException(status_code=400, detail="Tag already exists")

    db_tag = Tag(
        name=name,
    )
    db_session.add(db_tag)
    db_session.commit()
    db_session.refresh(db_tag)
    return db_tag


@tag_router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    tag = db_session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete tags."
        )
    db_session.delete(tag)
    db_session.commit()
    return {"status": "ok"}


@tag_router.patch("/{tag_id}")
async def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db_session: Session = Depends(get_session),
    current_user: User = Security(get_current_user),
):
    db_tag = db_session.get(Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if current_user.user_role != UserRole.PLATFORM_ADMINISTRATOR:
        raise HTTPException(
            status_code=403, detail="You do not have permission to update tags."
        )
    db_tag.sqlmodel_update(tag.model_dump(exclude_unset=True))
    db_session.commit()
    db_session.refresh(db_tag)
    return db_tag
