import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    currency = Column(String(3), nullable=False)  # e.g. USD, EUR
    balance = Column(Numeric(18, 2), nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
