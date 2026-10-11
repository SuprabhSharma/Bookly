import logging
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.config import Config

passwd_context = CryptContext(
    schemes=['bcrypt']
)

ACCESS_TOKEN_EXPIRY = 3600


def normalize_email(email: str) -> str:
    """Return the canonical form used for email lookups and storage."""
    return email.strip().lower()

def generate_password_hash(password : str) -> str:
    hash = passwd_context.hash(password)
    
    return hash 

def verify_password(password : str , hash : str ) -> bool:
    return passwd_context.verify(password , hash)


def create_access_tokens(user_data : dict , expiry : timedelta = None , refresh : bool = False):
    
    payload = {}
    
    payload['user'] = user_data
    payload['exp'] = datetime.now(timezone.utc) + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh
    
    token = jwt.encode(
        payload = payload,
        key = Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    
    return token


def decode_token(token : str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )
        return token_data

    except (jwt.PyJWTError, TypeError, ValueError) as exc:
        # A bad token is a client authentication error, not an application
        # failure. Keep the reason in the server log without a traceback for
        # expected malformed/expired tokens.
        logging.warning("Unable to decode access token: %s", exc)
        return None
