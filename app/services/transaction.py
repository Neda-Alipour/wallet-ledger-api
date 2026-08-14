from uuid import UUID
from pydantic import TypeAdapter

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from decimal import Decimal

from app.models.transaction import Transaction
from app.models.ledger import LedgerEntry
from app.models.user import User

from app.models.wallet import Wallet
from app.schemas.transaction import RecentTransactionRead, TransactionStatus, TransactionType

from app.services.wallet import WalletService


class InvalidTransferError(Exception):
    pass

class WalletCurrencyMismatchError(Exception):
    pass

class SameWalletTransferError(Exception):
    pass



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
            # 1. Verify the wallet belongs to current user
            self.wallet_service.get_wallet_by_user_id(
                user_id=user_id,
                wallet_id=wallet_id,
            )
            
            transaction = create_transaction(
                self.db,
                transaction_type=TransactionType.DEPOSIT,
                reference=reference,
            )

            wallet = self.wallet_service.increase_balance(
                wallet_id=wallet_id,
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


    def withdraw(
        self,
        user_id: UUID,
        wallet_id: UUID,
        amount: Decimal,
        reference: str | None = None,
    ):
        try:
            # 1. Verify the wallet belongs to current user
            self.wallet_service.get_wallet_by_user_id(
                user_id=user_id,
                wallet_id=wallet_id,
            )

            transaction = create_transaction(
                self.db,
                transaction_type=TransactionType.WITHDRAWAL,
                reference=reference,
            )

            wallet = self.wallet_service.decrease_balance(
                wallet_id=wallet_id,
                amount=amount,
            )

            ledger_entry = create_ledger_entry(
                self.db,
                wallet_id=wallet.id,
                transaction_id=transaction.id,
                amount=-amount, # the difference between deposit and withdrawal
            )

            self.db.commit()

            self.db.refresh(transaction)
            self.db.refresh(ledger_entry)
            self.db.refresh(wallet)

            return transaction, ledger_entry, wallet

        except Exception:
            self.db.rollback()
            raise


    def transfer(
        self,
        user_id: UUID,
        source_wallet_id: UUID,
        destination_wallet_id: UUID,
        amount: Decimal,
        reference: str | None = None,
    ):

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if source_wallet_id == destination_wallet_id:
            raise InvalidTransferError(
                "Source and destination wallets must be different."
            )

        try:

            # 1. Verify SOURCE wallet belongs to current user
            source_wallet = self.wallet_service.get_wallet_by_user_id(
                user_id=user_id,
                wallet_id=source_wallet_id,
            )

            # 2. Find DESTINATION wallet
            # IMPORTANT:
            # We intentionally DO NOT check user_id here.
            # The destination belongs to another user.
            destination_wallet = self.wallet_service.get_wallet_by_id(
                wallet_id=destination_wallet_id,
            )

            # 3. Make sure currencies match
            if source_wallet.currency != destination_wallet.currency:
                raise WalletCurrencyMismatchError(
                    "Source and destination wallets must use "
                    "the same currency."
                )

            # 4. Create ONE transaction
            transaction = create_transaction(
                self.db,
                transaction_type=TransactionType.TRANSFER,
                reference=reference,
            )

            # 5. Decrease source wallet
            source_wallet = self.wallet_service.decrease_balance(
                wallet_id=source_wallet.id,
                amount=amount,
            )

            # 6. Increase destination wallet
            destination_wallet = self.wallet_service.increase_balance(
                wallet_id=destination_wallet.id,
                amount=amount,
            )

            # 7. Create SOURCE ledger entry
            source_entry = create_ledger_entry(
                self.db,
                wallet_id=source_wallet.id,
                transaction_id=transaction.id,
                amount=-amount,
            )

            # 8. Create DESTINATION ledger entry
            destination_entry = create_ledger_entry(
                self.db,
                wallet_id=destination_wallet.id,
                transaction_id=transaction.id,
                amount=amount,
            )

            # 9. Commit EVERYTHING together
            self.db.commit()

            self.db.refresh(transaction)
            self.db.refresh(source_entry)
            self.db.refresh(destination_entry)
            self.db.refresh(source_wallet)
            self.db.refresh(destination_wallet)

            return (
                transaction,
                source_wallet,
                destination_wallet,
            )

        except Exception:
            self.db.rollback()
            raise