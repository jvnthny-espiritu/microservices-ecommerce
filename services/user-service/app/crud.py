from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas
from passlib.context import CryptContext

# Use argon2 (recommended). If you switched back to bcrypt, change the scheme here.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Return a user model (or None) for the given email."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Create a new user.
    user_in.password is a SecretStr (Pydantic). Use get_secret_value() to access raw string.
    """
    raw_password = user_in.password.get_secret_value()
    hashed = pwd_context.hash(raw_password)
    db_user = models.User(email=user_in.email, hashed_password=hashed, full_name=user_in.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user by email and password.
    Returns the user model on success, otherwise None.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user