from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from argon2 import PasswordHasher, exceptions as argon2_exceptions
from sqlmodel import Session

from ludika_backend.models.users import User
from ludika_backend.utils.config import get_config_value
from ludika_backend.utils.db import get_session

SECRET_KEY = get_config_value("Authentication", "secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_config_value("Authentication", "access_token_expire_minutes"))
ALGORITHM = "HS256"

argon2_hasher = PasswordHasher()

OAUTH2_LOGIN_URL = "/api/v1/auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH2_LOGIN_URL)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=OAUTH2_LOGIN_URL, auto_error=False)


def create_access_token(data: dict, start_time: datetime, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = start_time + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def hash_password(password: str) -> str:
    return argon2_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return argon2_hasher.verify(hashed, password)
    except argon2_exceptions.VerifyMismatchError:
        return False


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, user_id)
    if user is None or not user.enabled:
        raise credentials_exception

    return user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme_optional), session: Session = Depends(get_session)
) -> User | None:
    if token is None:
        return None

    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = session.get(User, user_id)
        if user is None or not user.enabled:
            raise credentials_exception
        return user
    except JWTError:
        return None
