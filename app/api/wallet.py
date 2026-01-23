from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

def require_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user_id

@router.get("/wallet", response_class=HTMLResponse)
def wallet(
    request: Request, 
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    wallet, user = db.query(Wallet, User).join(User, Wallet.user_id == User.id).filter(User.id == user_id).first()

    print(f"Wallet Balance: {wallet.balance}")
    print(f"Username: {user.email}")

    return templates.TemplateResponse("wallet.html", {
        "request": request, 
        "user": user,
        "wallet": wallet,
    })