from datetime import datetime, timedelta, timezone
from jose import jwt

from argon2 import PasswordHasher, exceptions as argon2_exceptions

from ludika_backend.util.config import get_config_value

SECRET_KEY = get_config_value("Authentication", "secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    get_config_value("Authentication", "access_token_expire_minutes")
)
ALGORITHM = "HS256"

argon2_hasher = PasswordHasher()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
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
