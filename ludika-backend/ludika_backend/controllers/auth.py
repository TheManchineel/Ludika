# auth.py
from fastapi import HTTPException, Cookie
from authlib.integrations.starlette_client import OAuth
from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError, JWTError

from ludika_backend.util.config import get_config_value

OAUTH_CLIENT_ID = get_config_value("GoogleAuth", "client_id")
OAUTH_CLIENT_SECRET = get_config_value("GoogleAuth", "client_secret")
OAUTH_SECRET_KEY = get_config_value("GoogleAuth", "secret_key")
OAUTH_REDIRECT_URI = f"{get_config_value("Server", "base_url")}/auth/login/callback"
OAUTH_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
OAUTH_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
OAUTH_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
OAUTH_SCOPE = "openid profile email"

JWT_SECRET_KEY = get_config_value("GoogleAuth", "jwt_secret_key")
ALGORITHM = "HS256"

__oauth: OAuth | None = None


def get_oauth() -> OAuth:
    """
    Returns an OAuth instance for Google authentication.
    """
    global __oauth
    if __oauth:
        return __oauth

    # OAuth Setup
    __oauth = OAuth()
    __oauth.register(
        name="ludika",
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        authorize_url=OAUTH_AUTHORIZE_URL,
        authorize_params=None,
        access_token_url=OAUTH_ACCESS_TOKEN_URL,
        access_token_params=None,
        refresh_token_url=None,
        authorize_state=OAUTH_SECRET_KEY,
        redirect_uri=OAUTH_REDIRECT_URI,
        jwks_uri=OAUTH_JWKS_URL,
        client_kwargs={"scope": OAUTH_SCOPE},
    )
    return __oauth


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(days=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload.get("sub"), "email": payload.get("email")}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
