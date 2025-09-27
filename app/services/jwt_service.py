from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from app.config import get_settings
from app.utils.global_logging import get_logger

settings = get_settings()

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algo

logger = get_logger(__name__)


class JWTService:
    def __init__(self):
        pass

    def create_token(self, data: Dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    def verify_token(self, token: str) -> Any:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload


jwt_service = JWTService()
