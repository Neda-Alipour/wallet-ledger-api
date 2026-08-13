from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionRead(BaseModel):

    type: TransactionType
    status: TransactionStatus
    reference: str | None
    created_at: datetime


class RecentTransactionRead(TransactionRead):
    transaction_id: UUID
    wallet_id: UUID
    amount: Decimal


class RecentTransactionsRead(BaseModel):
    transactions: list[RecentTransactionRead]


class DepositCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=18,
        decimal_places=2
    )

