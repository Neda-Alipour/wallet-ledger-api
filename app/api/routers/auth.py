from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import AuthBase
from app.schemas.user import UserRead
from app.services.auth import UserAlreadyExistsError, WeakPasswordError

from app.db.redis_db import add_jti_to_blacklist
from app.schemas.dependencies import get_access_token, AuthServiceDep


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead)
def signup(
    credentials: AuthBase,
    auth_service: AuthServiceDep,
):
    try:
        user = auth_service.create_user_with_wallets(credentials)

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        )

    return user


@router.post("/login")
def login(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
):

    token = auth_service.authenticate_user(
        email=request_form.username, password=request_form.password
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {
        "access_token": token,
        "type": "jwt",
    }


@router.get("/logout")
def logout_user(
    token_data: Annotated[dict, Depends(get_access_token)],
):
    add_jti_to_blacklist(token_data["jti"])
    return {"details": "Logged out"}
