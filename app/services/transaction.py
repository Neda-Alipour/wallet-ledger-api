from uuid import UUID
from pydantic import TypeAdapter

from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from decimal import Decimal

from app.models.transaction import Transaction
from app.models.ledger import LedgerEntry

from app.schemas.transaction import (
    RecentTransactionRead,
    TransactionStatus,
    TransactionType,
)

from app.services.wallet import WalletService


def create_transaction(
    db: Session,
    transaction_type: TransactionType,
    reference: str | None = None,
) -> Transaction:

    transaction = Transaction(
        type=transaction_type,
        status=TransactionStatus.COMPLETED,
        reference=reference,
    )

    db.add(transaction)
    db.flush()

    return transaction


def create_ledger_entry(
    db: Session,
    wallet_id: UUID,
    transaction_id: UUID,
    amount: Decimal,
) -> LedgerEntry:

    entry = LedgerEntry(
        wallet_id=wallet_id,
        transaction_id=transaction_id,
        amount=amount,
    )

    db.add(entry)
    db.flush()

    return entry


# extra info: A transaction creates one or more ledger entries.


class TransactionService:
    def __init__(
        self,
        db: Session,
        wallet_service: WalletService,
    ):
        self.db = db
        self.wallet_service = wallet_service

    def get_recent_transactions(
        self,
        wallet_id: UUID | None = None,
        limit: int = 20,
    ):

        stmt = (
            select(
                Transaction.id.label("transaction_id"),
                Transaction.type,
                Transaction.status,
                LedgerEntry.amount,
                LedgerEntry.wallet_id,
                Transaction.reference,
                Transaction.created_at,
            )
            .join(
                LedgerEntry,
                LedgerEntry.transaction_id == Transaction.id,
            )
            .where(
                LedgerEntry.wallet_id == wallet_id,
            )
            .order_by(LedgerEntry.created_at.desc())
            .limit(limit)
        )

        rows = self.db.execute(stmt).mappings().all()

        return TypeAdapter(list[RecentTransactionRead]).validate_python(rows)

    def deposit(
        self,
        user_id: UUID,
        wallet_id: UUID,
        amount: Decimal,
        reference: str | None = None,
    ):
        try:
            transaction = create_transaction(
                self.db,
                transaction_type=TransactionType.DEPOSIT,
                reference=reference,
            )

            wallet = self.wallet_service.increase_balance(
                wallet_id=wallet_id,
                user_id=user_id,
                amount=amount,
            )

            ledger_entry = create_ledger_entry(
                self.db,
                wallet_id=wallet.id,
                transaction_id=transaction.id,
                amount=amount,
            )

            # Commit everything together
            self.db.commit()

            # Refresh objects if you need database-generated values
            self.db.refresh(transaction)
            self.db.refresh(ledger_entry)
            self.db.refresh(wallet)

            return transaction, ledger_entry, wallet

        except Exception:
            self.db.rollback()
            raise
