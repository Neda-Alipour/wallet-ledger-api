from typing import Annotated
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.ledger import LedgerEntry

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

# Define a reusable type
db_dependency = Annotated[Session, Depends(get_db)]

def require_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        # best practice for fastapi
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user_id

def _coerce_uuid(value) -> UUID:
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session user_id")

@router.get("/", response_class=HTMLResponse, name="home")
@router.get("/wallet", response_class=HTMLResponse, name="wallet")
def wallet(
    request: Request, 
    db: db_dependency,
    user_id=Depends(require_user)
):
    user_id = _coerce_uuid(user_id)
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    result = db.execute(select(Wallet).where(Wallet.user_id == user_id).order_by(Wallet.created_at.asc()))
    wallets = result.scalars().all()

    if not wallets:
        # if you always create on signup, this may never happen; still safer to handle.
        return RedirectResponse(url="/wallet?error=No wallet found", status_code=303)

    wallet_id_param = request.query_params.get("wallet_id")
    active_wallet = None
    if wallet_id_param:
        try:
            wid = UUID(wallet_id_param)
            active_wallet = next((w for w in wallets if w.id == wid), None)
        except Exception:
            active_wallet = None

    if active_wallet is None:
        active_wallet = wallets[0]

    stmt = (
        select(LedgerEntry, Transaction)
        .join(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .where(LedgerEntry.wallet_id == active_wallet.id)
        .order_by(LedgerEntry.created_at.desc())
        .limit(20)
    )

    # Returns a list of Row objects (which behave like tuples)
    recent = db.execute(stmt).all()

    return templates.TemplateResponse("wallet.html", {
        "request": request, 
        "user": user,
        "wallet": active_wallet,
        "wallets": wallets,
        "recent": recent,
    })

@router.post("/wallet/deposit")
def deposit(
    request: Request,
    db: db_dependency,
    amount: Decimal = Form(...),
    reference: str | None = Form(None),
    user_id=Depends(require_user),
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")

    user_id = _coerce_uuid(user_id)

    try:
        with db.begin():
            tx = Transaction(type="deposit", status="completed", reference=reference)
            db.add(tx)
            db.flush()  # ensures tx.id is available

            # Atomic balance update (race-safe)
            stmt = (
                update(Wallet)
                .where(Wallet.user_id == user_id)
                .values(balance=Wallet.balance + amount)
                .returning(Wallet.id, Wallet.balance)
            )
            row = db.execute(stmt).first()
            if row is None:
                raise HTTPException(status_code=404, detail="Wallet not found")

            wallet_id, new_balance = row

            db.add(LedgerEntry(
                wallet_id=wallet_id,
                transaction_id=tx.id,
                amount=amount,  # credit
            ))

        return {
            "transaction_id": str(tx.id),
            "wallet_id": str(wallet_id),
            "balance": str(new_balance),
        }

    except IntegrityError:
        # likely duplicate reference (transactions.reference is unique)
        raise HTTPException(status_code=409, detail="Duplicate transaction reference")


@router.post("/wallet/withdraw")
def withdraw(
    request: Request,
    db: db_dependency,
    amount: Decimal = Form(...),
    reference: str | None = Form(None),
    user_id=Depends(require_user),
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")

    user_id = _coerce_uuid(user_id)

    try:
        with db.begin():
            tx = Transaction(type="withdrawal", status="completed", reference=reference)
            db.add(tx)
            db.flush()

            # Atomic conditional update prevents overdraft + prevents race conditions
            stmt = (
                update(Wallet)
                .where(
                    Wallet.user_id == user_id,
                    Wallet.balance >= amount,
                )
                .values(balance=Wallet.balance - amount)
                .returning(Wallet.id, Wallet.balance)
            )
            row = db.execute(stmt).first()

            if row is None:
                # differentiate "no wallet" vs "insufficient funds"
                wallet_exists = db.execute(
                    select(Wallet.id).where(Wallet.user_id == user_id)
                ).first()
                if wallet_exists is None:
                    raise HTTPException(status_code=404, detail="Wallet not found")
                raise HTTPException(status_code=400, detail="Insufficient funds")

            wallet_id, new_balance = row

            db.add(LedgerEntry(
                wallet_id=wallet_id,
                transaction_id=tx.id,
                amount=-amount,  # debit
            ))

        return {
            "transaction_id": str(tx.id),
            "wallet_id": str(wallet_id),
            "balance": str(new_balance),
        }

    except IntegrityError:
        raise HTTPException(status_code=409, detail="Duplicate transaction reference")
    

# @router.post("/wallet/deposit")
# def deposit(
#     request: Request,
#     wallet_id: str = Form(...),
#     amount: Decimal = Form(...),
#     reference: str | None = Form(None),
#     user_id=Depends(require_user),
#     db: db_dependency,
# ):
#     if amount <= 0:
#         return RedirectResponse(url=f"/wallet?error=Amount must be > 0", status_code=303)

#     user_id = _coerce_uuid(user_id)
#     try:
#         wallet_uuid = UUID(wallet_id)
#     except Exception:
#         return RedirectResponse(url=f"/wallet?error=Invalid wallet_id", status_code=303)

#     try:
#         with db.begin():
#             # ensure wallet belongs to user
#             w = db.query(Wallet).filter(Wallet.id == wallet_uuid, Wallet.user_id == user_id).first()
#             if not w:
#                 return RedirectResponse(url="/wallet?error=Wallet not found", status_code=303)

#             tx = Transaction(type="deposit", status="completed", reference=reference)
#             db.add(tx)
#             db.flush()

#             stmt = (
#                 update(Wallet)
#                 .where(Wallet.id == wallet_uuid, Wallet.user_id == user_id)
#                 .values(balance=Wallet.balance + amount)
#                 .returning(Wallet.balance)
#             )
#             new_balance = db.execute(stmt).scalar_one()

#             db.add(LedgerEntry(
#                 wallet_id=wallet_uuid,
#                 transaction_id=tx.id,
#                 amount=amount,  # credit
#             ))

#         return RedirectResponse(url=f"/wallet?wallet_id={wallet_uuid}&success=Deposit successful", status_code=303)

#     except Exception:
#         # keep it simple for now; later you can map IntegrityError for duplicate reference etc.
#         return RedirectResponse(url=f"/wallet?wallet_id={wallet_uuid}&error=Deposit failed", status_code=303)


# @router.post("/wallet/withdraw")
# def withdraw(
#     request: Request,
#     wallet_id: str = Form(...),
#     amount: Decimal = Form(...),
#     reference: str | None = Form(None),
#     user_id=Depends(require_user),
#     db: db_dependency,
# ):
#     if amount <= 0:
#         return RedirectResponse(url=f"/wallet?error=Amount must be > 0", status_code=303)

#     user_id = _coerce_uuid(user_id)
#     try:
#         wallet_uuid = UUID(wallet_id)
#     except Exception:
#         return RedirectResponse(url=f"/wallet?error=Invalid wallet_id", status_code=303)

#     try:
#         with db.begin():
#             # Atomic conditional update (prevents race conditions + overdraft)
#             stmt = (
#                 update(Wallet)
#                 .where(
#                     Wallet.id == wallet_uuid,
#                     Wallet.user_id == user_id,
#                     Wallet.balance >= amount,
#                 )
#                 .values(balance=Wallet.balance - amount)
#                 .returning(Wallet.balance)
#             )
#             row = db.execute(stmt).first()
#             if row is None:
#                 # check if wallet exists (to show correct error)
#                 exists = db.query(Wallet.id).filter(Wallet.id == wallet_uuid, Wallet.user_id == user_id).first()
#                 if not exists:
#                     return RedirectResponse(url="/wallet?error=Wallet not found", status_code=303)
#                 return RedirectResponse(url=f"/wallet?wallet_id={wallet_uuid}&error=Insufficient funds", status_code=303)

#             new_balance = row[0]

#             tx = Transaction(type="withdrawal", status="completed", reference=reference)
#             db.add(tx)
#             db.flush()

#             db.add(LedgerEntry(
#                 wallet_id=wallet_uuid,
#                 transaction_id=tx.id,
#                 amount=-amount,  # debit
#             ))

#         return RedirectResponse(url=f"/wallet?wallet_id={wallet_uuid}&success=Withdrawal successful", status_code=303)

#     except Exception:
#         return RedirectResponse(url=f"/wallet?wallet_id={wallet_uuid}&error=Withdrawal failed", status_code=303)


# The "Session State" Visualized
# Step Signup (Crashes) | Deposit (Works)
# Line 1 db.query(User) → Starts | Txif amount <= 0 → Idle
# Line 2 if existing: → Active | Tx_coerce_uuid() → Idle
# Line 3 with db.begin() → ERROR | with db.begin() → Starts Tx