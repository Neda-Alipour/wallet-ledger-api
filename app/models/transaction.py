import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    type = Column(String, nullable=False)  # deposit, withdrawal, transfer
    status = Column(String, nullable=False, default="pending")

    reference = Column(String, unique=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
