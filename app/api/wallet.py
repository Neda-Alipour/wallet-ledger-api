from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
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
        # best practice for fastapi
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user_id

@router.get("/wallet", response_class=HTMLResponse)
def wallet(
    request: Request, 
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
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