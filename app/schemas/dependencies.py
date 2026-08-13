from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.auth import AuthService
from app.services.transaction import TransactionService
from app.services.wallet import WalletService

from app.core.security import oauth2_scheme
from app.utils import decode_access_token
from app.db.redis_db import is_jti_blacklisted

DatabaseDep = Annotated[Session, Depends(get_db)]


def get_wallet_service(db: DatabaseDep):
    return WalletService(db)


def get_auth_service(
    db: DatabaseDep,
    wallet_service: WalletService = Depends(get_wallet_service),
):
    return AuthService(
        db,
        wallet_service=wallet_service,
    )


def get_transaction_service(
    db: DatabaseDep,
    wallet_service: WalletService = Depends(get_wallet_service),
):
    return TransactionService(
        db=db,
        wallet_service=wallet_service,
    )


# Access token data dep
def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]):

    if not token or token.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = decode_access_token(token)

    if data is None or is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    return data


# Logged in user
def get_current_user(
    token_data: Annotated[dict, Depends(get_access_token)], db: DatabaseDep
) -> User:

    return db.get(User, UUID(token_data["user"]["id"]))


# User dep
UserDep = Annotated[User, Depends(get_current_user)]

# Auth Dep
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

# Transaction Dep
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]

# Wallet Dep
WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]

# why Annotated not just Session = Depends(get_db)? because we want to specify the type of db parameter as Session for better type hinting and editor support
