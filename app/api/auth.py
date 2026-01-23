from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.db.session import get_db
from app.models.user import User
from app.services.auth import hash_password, verify_password

router = APIRouter()

@router.post("/signup")
def signup(
    request: Request,
    # full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print("User already exists")
        return RedirectResponse(url="/signup", status_code=303)

    user = User(
        # full_name=full_name,
        email=email,
        hashed_password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = str(user.id)

    return RedirectResponse(url="/wallet", status_code=303)

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
 
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    elif not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/login", status_code=303)
    
    request.session["user_id"] = str(user.id)

    return RedirectResponse(url="/wallet", status_code=303)
