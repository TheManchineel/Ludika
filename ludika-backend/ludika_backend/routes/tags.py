from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from ludika_backend.models.games import Tag
from ludika_backend.util.db import get_session

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
