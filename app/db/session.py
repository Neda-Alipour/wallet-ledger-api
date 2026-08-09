from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import db_settings

engine = create_engine(db_settings.DATABASE_URL, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()