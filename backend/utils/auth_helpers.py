import os
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import generate_password_hash, check_password_hash

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 24))
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")
    return generate_password_hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return check_password_hash(hashed_password, password)


def generate_token(email: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": email,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
