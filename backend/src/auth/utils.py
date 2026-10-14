import logging
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from src.config import Config

logger = logging.getLogger(__name__)

passwd_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600


def normalize_email(email: str) -> str:
    """Return the canonical form used for email lookups and storage."""
    return email.strip().lower()


def generate_passwd_hash(password: str) -> str:
    hash = passwd_context.hash(password)

    return hash



def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)


def create_access_tokens(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):

    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now(timezone.utc) + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )
        return token_data

    except (jwt.PyJWTError, TypeError, ValueError) as exc:
        logger.warning("Unable to decode access token: %s", exc)
        return None


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)


def create_url_safe_token(data: dict):

    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str, max_age: int):
    try:
        return serializer.loads(token, max_age=max_age)
    except Exception as exc:
        logger.warning("Unable to decode time-limited token: %s", exc)
        return None
