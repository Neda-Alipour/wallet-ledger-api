from datetime import datetime, timedelta, timezone

from uuid import uuid4
from fastapi import HTTPException, status
import jwt

from app.core.config import security_settings

def generate_access_token(
        data: dict,
        expiry: timedelta = timedelta(seconds=60)
):
    token = jwt.encode(
                payload={
                    **data,
                    "jti": str(uuid4()),
                    "exp": datetime.now(timezone.utc) + expiry
                },
                algorithm=security_settings.JWT_ALGORITHM,
                key=security_settings.JWT_SECRET,
            )
    return token

# dict because payload is a dictionary
def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            jwt=token,
            algorithms=[security_settings.JWT_ALGORITHM],
            key=security_settings.JWT_SECRET,

        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token")
    except jwt.PyJWKError:
        return None