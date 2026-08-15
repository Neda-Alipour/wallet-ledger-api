from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


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

    
class TransactionOperationRead(RecentTransactionRead):
    balance: Decimal
    currency: str


class RecentTransactionsRead(BaseModel):
    currency: str
    transactions: list[RecentTransactionRead]


class CreateTransaction(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=18,
        decimal_places=2
    )
    reference: str | None = None

    @field_validator("reference")
    @classmethod
    def empty_reference_to_none(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

        return value or None


class CreateTransfer(CreateTransaction):
    source_wallet_id: UUID
    destination_wallet_id: UUID


class TransferRead(TransactionOperationRead):
    destination_wallet_id: UUID
    # destination_balance: Decimal
