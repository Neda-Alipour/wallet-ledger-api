from passlib.context import CryptContext
from sqlalchemy import select
from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.wallet import WalletService

from app.schemas.auth import AuthBase
from app.schemas.wallet import Currency

from app.utils import generate_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_DUMMY_HASH = pwd_context.hash("dummy-password-for-timing-safety")


class UserAlreadyExistsError(Exception):
    pass


class WeakPasswordError(ValueError):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(db: Session, email: str, password: str) -> User:

    user = User(
        email=normalize_email(email),
        hashed_password=hash_password(password),
    )

    db.add(user)

    try:
        db.flush()  # Ensure the user ID is generated
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsError(email)

    return user


class AuthService:
    def __init__(
        self,
        db: Session,
        wallet_service: WalletService,
    ):
        self.db = db
        self.wallet_service = wallet_service

    def create_user_with_wallets(
        self,
        credentials: AuthBase,
        currencies: list[Currency] | None = None,
    ) -> User:

        # Session.begin() used as a context manager already commits on success and rolls back on exception.
        try:
            with self.db.begin():
                user = create_user(
                    self.db,
                    credentials.email,
                    credentials.password,
                )

                self.wallet_service.create_wallets(
                    str(user.id),
                    currencies=currencies,
                )

        except UserAlreadyExistsError:
            raise
        except IntegrityError:
            # e.g. concurrent signup hit the unique constraint
            raise UserAlreadyExistsError(credentials.email)

        # Detach so caller can use it after commit without refresh errors
        self.db.refresh(user)

        return user

    def authenticate_user(self, email: str, password: str) -> str | None:

        normalized_email = normalize_email(email)

        stmt = select(User).where(User.email == normalized_email)
        # More idiomatic than .scalars().first(), and it will raise if the query unexpectedly returns multiple rows (which would indicate a data integrity bug, e.g., missing unique constraint on email).
        user = self.db.execute(stmt).scalar_one_or_none()

        # if not user or not verify_password(password, user.hashed_password):
        #     return None
        # If the user doesn't exist, verify_password (bcrypt hashing) is skipped entirely, so the response time for "no such user" is much faster than "wrong password". An attacker can use this timing difference to enumerate valid emails.

        # This ensures verify_password (the slow bcrypt call) always runs, regardless of whether the user exists.
        hashed = user.hashed_password if user else _DUMMY_HASH
        valid = verify_password(password, hashed)

        if not user or not valid:
            return None

        token = generate_access_token(
            data={
                "user": {
                    "name": user.email,  # change it to name later
                    "id": str(user.id),
                }
            }
        )

        return token


# why execute select? why not just query all? because SQLAlchemy 2.0 style uses select() statements instead of query() method for better clarity and performance.
# user = db.query(User).filter(User.email == form.email).first()


# def get_current_user(
#     request: Request,
#     db: DatabaseDep
# ):
#     user_id = request.session.get("user_id")

#     if not user_id:
#         raise HTTPException(401, "Not authenticated")

#     user = db.get(User, user_id)
#     if not user:
#         raise HTTPException(401, "User not found")

#     return user
