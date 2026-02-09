from typing import Annotated
from passlib.context import CryptContext
from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# Define a reusable type
db_dependency = Annotated[Session, Depends(get_db)]

def get_current_user(
    request: Request,
    db: db_dependency
):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(401, "Not authenticated")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")

    return user