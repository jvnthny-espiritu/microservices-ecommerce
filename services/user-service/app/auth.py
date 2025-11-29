import os
import secrets
import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import crud, models
from .database import get_db

# Minimum 32 bytes (256 bits) recommended for HS256
MIN_SECRET_LENGTH = 32

def _get_jwt_secret() -> str:
    """Get JWT secret with validation for production use."""
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        # Generate secure default for development only
        secret = secrets.token_urlsafe(32)
        warnings.warn(
            "JWT_SECRET not set. Using auto-generated secret. "
            "Set JWT_SECRET env var with 32+ random bytes for production.",
            UserWarning,
        )
    elif len(secret) < MIN_SECRET_LENGTH:
        warnings.warn(
            f"JWT_SECRET is too short ({len(secret)} chars). "
            f"Use at least {MIN_SECRET_LENGTH} random bytes for production security.",
            UserWarning,
        )
    return secret

JWT_SECRET = _get_jwt_secret()
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
