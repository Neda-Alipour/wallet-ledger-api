from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.ledger import LedgerEntry

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

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

@router.get("/wallet", response_class=HTMLResponse)
def wallet(
    request: Request, 
    user_id=Depends(require_user),
    db: Session = Depends(get_db)
):
    user_id = _coerce_uuid(user_id)
    
    result = (
        db.query(Wallet, User)
        .join(User, Wallet.user_id == User.id)
        .filter(User.id == user_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    
    wallet, user = result

    # print(f"Wallet Balance: {wallet.balance}")
    # print(f"Username: {user.email}")

    return templates.TemplateResponse("wallet.html", {
        "request": request, 
        "user": user,
        "wallet": wallet,
    })

@router.post("/wallet/deposit")
def deposit(
    request: Request,
    amount: Decimal = Form(...),
    reference: str | None = Form(None),
    user_id=Depends(require_user),
    db: Session = Depends(get_db),
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
    amount: Decimal = Form(...),
    reference: str | None = Form(None),
    user_id=Depends(require_user),
    db: Session = Depends(get_db),
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