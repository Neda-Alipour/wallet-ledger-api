from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.schemas.dependencies import UserDep, TransactionServiceDep, WalletServiceDep
from app.schemas.wallet import WalletReadItem, WalletsRead
from app.schemas.transaction import (
    CreateTransaction,
    RecentTransactionsRead,
    TransactionOperationRead,
    CreateTransfer,
    TransferRead,
)
from app.services.wallet import WalletNotFoundError, InsufficientBalanceError
from app.services.transaction import WalletCurrencyMismatchError, InvalidTransferError


router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get(
    "/",
    name="wallet",
    response_model=WalletsRead,
)
def wallet(
    user: UserDep,
    wallet_service: WalletServiceDep,
    wallet_id: UUID | None = None,
):
    wallets = user.wallets
    # if we always create wallet on signup, this may never happen; still safer to handle.
    if not wallets:
        raise HTTPException(
            status_code=404,
            detail="No wallets found.",
        )

    try:
        active_wallet = wallet_service.get_active_wallet(
            user=user,
            wallet_id=wallet_id,
        )

        return WalletsRead(
            wallet=active_wallet,
            wallets=wallets,
        )

    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )


@router.get(
    "/transactions",
    name="transactions",
    response_model=RecentTransactionsRead,
)
def transactions(
    user: UserDep,
    wallet_service: WalletServiceDep,
    transaction_service: TransactionServiceDep,
    wallet_id: UUID | None = None,
    limit: int | None = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    try:
        active_wallet = wallet_service.get_active_wallet(
            user=user,
            wallet_id=wallet_id,
        )

        transactions = transaction_service.get_recent_transactions(
            wallet_id=active_wallet.id,
            limit=limit,
        )

        return RecentTransactionsRead(
            transactions=transactions,
            currency=active_wallet.currency
        )
    
    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )


@router.post(
    "/deposit",
    response_model=TransactionOperationRead,
)
def deposit(
    user: UserDep,
    data: CreateTransaction,
    wallet_id: UUID,
    service: TransactionServiceDep,
):
    try:
        transaction, ledger_entry, wallet = service.deposit(
            user_id=user.id,
            wallet_id=wallet_id,
            amount=data.amount,
            reference=data.reference,
        )

        return TransactionOperationRead(
            transaction_id=transaction.id,
            wallet_id=wallet.id,
            currency=wallet.currency,
            amount=ledger_entry.amount,
            balance=wallet.balance,
            type=transaction.type,
            status=transaction.status,
            reference=transaction.reference,
            created_at=transaction.created_at,
        )

    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Transaction reference already exists.",
        )


@router.post(
    "/withdraw",
    response_model=TransactionOperationRead,
)
def withdraw(
    user: UserDep,
    data: CreateTransaction,
    wallet_id: UUID,
    service: TransactionServiceDep,
):
    try:
        transaction, ledger_entry, wallet = service.withdraw(
            user_id=user.id,
            wallet_id=wallet_id,
            amount=data.amount,
            reference=data.reference,
        )

        return TransactionOperationRead(
            transaction_id=transaction.id,
            wallet_id=wallet.id,
            currency=wallet.currency,
            amount=ledger_entry.amount,
            balance=wallet.balance,
            type=transaction.type,
            status=transaction.status,
            reference=transaction.reference,
            created_at=transaction.created_at,
        )

    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )

    except InsufficientBalanceError:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance.",
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Transaction reference already exists.",
        )


@router.post(
    "/transfer",
    response_model=TransferRead,
)
def transfer(
    user: UserDep,
    data: CreateTransfer,
    service: TransactionServiceDep,
):
    try:
        (
            transaction,
            source_wallet,
            destination_wallet,
        ) = service.transfer(
            user_id=user.id,
            source_wallet_id=data.source_wallet_id,
            destination_wallet_id=data.destination_wallet_id,
            amount=data.amount,
            reference=data.reference,
        )

        return TransferRead(
            transaction_id=transaction.id,
            wallet_id=source_wallet.id,
            currency=source_wallet.currency,
            destination_wallet_id=destination_wallet.id,
            amount=data.amount,
            balance=source_wallet.balance,
            type=transaction.type,
            status=transaction.status,
            reference=transaction.reference,
            created_at=transaction.created_at,
        )

    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )

    except InsufficientBalanceError:
        raise HTTPException(
            status_code=400,
            detail="Insufficient wallet balance.",
        )

    except WalletCurrencyMismatchError:
        raise HTTPException(
            status_code=400,
            detail="Source and destination wallets must use the same currency.",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except InvalidTransferError:
        raise HTTPException(
            status_code=400,
            detail="Source and destination wallets must be different.",
        )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Transaction reference already exists.",
        )
