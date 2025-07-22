from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session

from ludika_backend.controllers.auth import (
    hash_password,
    verify_password,
    create_access_token,
)
from ludika_backend.models.auth import AuthToken
from ludika_backend.models.users import UserPublic, UserCreate, User
from ludika_backend.util.db import get_session

auth_router = APIRouter()


@auth_router.post("/signup", response_model=UserPublic)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password.get_secret_value())
    db_user = User(
        uuid=uuid4(),
        email=user.email,
        visible_name=user.visible_name,
        created_at=datetime.now(timezone.utc),
        password_hash=hashed_pw,
        user_role="user",
        enabled=True,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@auth_router.post("/login", response_model=AuthToken)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.uuid)})
    return AuthToken(access_token=access_token)
