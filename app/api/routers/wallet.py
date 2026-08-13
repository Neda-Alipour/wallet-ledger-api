from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from fastapi.templating import Jinja2Templates

from app.schemas.dependencies import DatabaseDep, UserDep, TransactionServiceDep, WalletServiceDep
from app.schemas.wallet import WalletReadItem, WalletsRead
from app.schemas.transaction import DepositCreate, RecentTransactionRead, RecentTransactionsRead
from app.services.wallet import WalletNotFoundError



router = APIRouter(tags=["wallet"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", name="home")
@router.get(
    "/wallet",
    name="wallet",
    response_model=WalletReadItem,
)
def wallet(
    user: UserDep,
    wallet_service: WalletServiceDep,
    wallet_id: UUID | None = None,
):

    # wallets = user.wallets
    # # if we always create wallet on signup, this may never happen; still safer to handle.
    # if not wallets:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="No wallets found.",
    #     )
    try:
        active_wallet = wallet_service.get_active_wallet(
            user=user,
            wallet_id=wallet_id,
        )

        return active_wallet
    
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
    limit: int | None = Query(
        default=20,
        ge=1,
        le=100,
    ),
    wallet_id: UUID | None = None,
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
        )
    except WalletNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found.",
        )



@router.post(
    "/wallet/deposit",
    response_model=RecentTransactionRead,
)
def deposit(
    user: UserDep,
    data: DepositCreate,
    wallet_id: UUID,
    service: TransactionServiceDep,
):
    try:
        transaction, ledger_entry, wallet = service.deposit(
            user_id=user.id,
            wallet_id=wallet_id,
            amount=data.amount,
        )

        return RecentTransactionRead(
            transaction_id=transaction.id,
            wallet_id=wallet.id,
            amount=ledger_entry.amount,
            status=transaction.status,
            type=transaction.type,
            reference=None,
            created_at=transaction.created_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    # if data.amount <= 0:
    #     raise HTTPException(status_code=400, detail="Amount must be > 0")

    # try:
    #     with db.begin():
    #         tx = Transaction(type="deposit", status="completed", reference=reference)
    #         db.add(tx)
    #         db.flush()  # ensures tx.id is available

    #         # Atomic balance update (race-safe)
    #         stmt = (
    #             update(Wallet)
    #             .where(Wallet.user_id == user.id)
    #             .values(balance=Wallet.balance + data.amount)
    #             .returning(Wallet.id, Wallet.balance)
    #         )
    #         row = db.execute(stmt).first()
    #         if row is None:
    #             raise HTTPException(status_code=404, detail="Wallet not found")

    #         wallet_id, new_balance = row

    #         db.add(LedgerEntry(
    #             wallet_id=wallet_id,
    #             transaction_id=tx.id,
    #             amount=data.amount,  # credit
    #         ))

    #     # request.session["success"] = f"Deposit successful. New balance: {new_balance}"
    #     details = f"Deposit successful. New balance: {new_balance}"

    #     return {
    #         "transaction_id": str(tx.id),
    #         "wallet_id": str(wallet_id),
    #         "balance": str(new_balance),
    #     }

    # except IntegrityError:
    #     # likely duplicate reference (transactions.reference is unique)
    #     raise HTTPException(status_code=409, detail="Duplicate transaction reference")


# @router.post("/wallet/withdraw")
# def withdraw(
#     db: DatabaseDep,
#     amount: Decimal = Form(...),
#     reference: str | None = Form(None),
# ):
#     if amount <= 0:
#         raise HTTPException(status_code=400, detail="Amount must be > 0")

#     # user_id = _coerce_uuid(user_id)

#     try:
#         with db.begin():
#             tx = Transaction(type="withdrawal", status="completed", reference=reference)
#             db.add(tx)
#             db.flush()

#             # Atomic conditional update prevents overdraft + prevents race conditions
#             stmt = (
#                 update(Wallet)
#                 .where(
#                     Wallet.user_id == user_id,
#                     Wallet.balance >= amount,
#                 )
#                 .values(balance=Wallet.balance - amount)
#                 .returning(Wallet.id, Wallet.balance)
#             )
#             row = db.execute(stmt).first()

#             if row is None:
#                 # differentiate "no wallet" vs "insufficient funds"
#                 wallet_exists = db.execute(
#                     select(Wallet.id).where(Wallet.user_id == user_id)
#                 ).first()
#                 if wallet_exists is None:
#                     raise HTTPException(status_code=404, detail="Wallet not found")
#                 raise HTTPException(status_code=400, detail="Insufficient funds")

#             wallet_id, new_balance = row

#             db.add(LedgerEntry(
#                 wallet_id=wallet_id,
#                 transaction_id=tx.id,
#                 amount=-amount,  # debit
#             ))

#         details = f"Withdrawal successful. New balance: {new_balance}"

#         return {
#             "transaction_id": str(tx.id),
#             "wallet_id": str(wallet_id),
#             "balance": str(new_balance),
#         }

#     except IntegrityError:
#         raise HTTPException(status_code=409, detail="Duplicate transaction reference")


# The "Session State" Visualized
# Step Signup (Crashes) | Deposit (Works)
# Line 1 db.query(User) → Starts | Txif amount <= 0 → Idle
# Line 2 if existing: → Active | Tx_coerce_uuid() → Idle
# Line 3 with db.begin() → ERROR | with db.begin() → Starts Tx


# ledger_entries = (
#         select(LedgerEntry)
#         .where(LedgerEntry.wallet_id == active_wallet.id)
#         .order_by(LedgerEntry.created_at.asc())
#     )
# recent_ledger_entries = db.execute(ledger_entries).scalars().all()
# print(recent_ledger_entries[1].transaction)

# Get recent ledger entries


# def _coerce_uuid(value) -> UUID:
#     try:
#         return value if isinstance(value, UUID) else UUID(str(value))
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid session user_id")

# def require_user(request: Request):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         # best practice for fastapi
#         raise HTTPException(
#             status_code=status.HTTP_303_SEE_OTHER,
#             headers={"Location": "/login"},
#         )
#     return _coerce_uuid(user_id)
