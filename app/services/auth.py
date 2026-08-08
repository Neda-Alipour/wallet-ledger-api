
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy import select
from app.models.user import User
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
# from app.schemas.dependencies import DatabaseDep

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_user(db: Session, email: str, password: str) -> User | None:
    # Check for existing user INSIDE the transaction for safety
    existing_user = db.execute(select(User).where(User.email == email)).scalars().first()
    if existing_user:
        return None

    hashed_password = hash_password(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.flush()  # Ensure the user ID is generated

    return user

def create_wallets(db: Session, user_id: str, currencies: list[str] | None = None):
    if currencies is None:
        currencies = ["USD", "EUR", "GBP"]
    for currency in currencies:
        wallet = Wallet(user_id=user_id, currency=currency, balance=0)
        db.add(wallet)
    db.flush()  # Ensure wallets are added


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user_with_wallets(self, email: str, password: str) -> User | None:

        # Use 'with db.begin_nested()' if a transaction has already started
        # OR just use the session directly since it handles the transaction

        try:
            # 1. Start the atomic block immediately
            with self.db.begin_nested():

                user = create_user(self.db, email, password)
                if user is None:
                    return None

                create_wallets(self.db, str(user.id), currencies=["USD", "EUR"])
                
                # NO NEED FOR db.commit() - it happens automatically here!
            # After the nested block finishes, we commit the whole session
            self.db.commit()

            return user
    
        except Exception as e:
            # NO NEED FOR db.rollback() - it happens automatically!
            print(f"Error creating user: {e}")
            return None

    def authenticate_user(self, email: str, password: str) -> User | None:
        # why execute select? why not just query all? because SQLAlchemy 2.0 style uses select() statements instead of query() method for better clarity and performance.
        # user = db.query(User).filter(User.email == form.email).first()
        user = self.db.execute(select(User).where(User.email == email)).scalars().first()

        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    

    
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