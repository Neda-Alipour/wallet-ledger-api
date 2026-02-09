from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.auth import SignupSchema, LoginSchema
from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.services.auth import hash_password, verify_password

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

# Define a reusable type
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
def signup(
    request: Request,
    db: db_dependency,
    form: SignupSchema = Depends(SignupSchema.as_form)
):
    # Use 'with db.begin_nested()' if a transaction has already started
    # OR just use the session directly since it handles the transaction
        
    try:
        # 1. Start the atomic block immediately
        with db.begin_nested():
            # Check for existing user INSIDE the transaction for safety
            result = db.execute(select(User).where(User.email == form.email))
            existing = result.scalars().first()
            
            if existing:
                return RedirectResponse(url="/signup", status_code=303)
        
            user = User(
                email=form.email,
                hashed_password=hash_password(form.password)
            )
            db.add(user)
            db.flush()  # Gets the user.id so the wallet can use it

            wallet = Wallet(
                user_id=user.id, 
                currency="USD", 
                balance=0
            )
            db.add(wallet)
            # NO NEED FOR db.commit() - it happens automatically here!
        # After the nested block finishes, we commit the whole session
        db.commit()

    except Exception as e:
        # NO NEED FOR db.rollback() - it happens automatically!
        print(f"Error creating user: {e}")
        return RedirectResponse(url="/signup", status_code=303)

    # 3. Finalize Session
    request.session["user_id"] = str(user.id)
    return RedirectResponse(url="/wallet", status_code=303)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    error = request.session.pop("error", None)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
        })

@router.post("/login")
# why Annotated not just Session = Depends(get_db)? because we want to specify the type of db parameter as Session for better type hinting and editor support 
def login(
    request: Request,
    db: db_dependency,
    form: LoginSchema = Depends(LoginSchema.as_form)
):
    # why execute select? why not just query all? because SQLAlchemy 2.0 style uses select() statements instead of query() method for better clarity and performance.
    # user = db.query(User).filter(User.email == form.email).first()
    result = db.execute(select(User).where(User.email == form.email))
    user = result.scalars().first()

    if not user:
        request.session["error"] = "User not found"
        return RedirectResponse(url="/login", status_code=303)
    elif not verify_password(form.password, user.hashed_password):
        request.session["error"] = "Incorrect password"
        return RedirectResponse(url="/login", status_code=303)
    
    request.session["user_id"] = str(user.id)

    return RedirectResponse(url="/wallet", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# Old version
# @router.post("/signup")
# def signup(
#     request: Request,
#     form: SignupSchema = Depends(SignupSchema.as_form),
#     db: db_dependency
# ):
    
#     existing = db.query(User).filter(User.email == form.email).first()
#     if existing:
#         print("User already exists")
#         return RedirectResponse(url="/signup", status_code=303)
      
#     try:
#         user = User(
#             # full_name=full_name,
#             email=form.email,
#             hashed_password=hash_password(form.password)
#         )
#         db.add(user)
#         db.flush()

#         wallet = Wallet(
#             user_id=user.id, 
#             currency="USD", 
#             balance=0
#         )
#         db.add(wallet)

#         db.commit()
#         db.refresh(user)

#     except Exception as e:
#         db.rollback()
#         print(f"Error creating user: {e}")
#         return RedirectResponse(url="/signup", status_code=303)

#     request.session["user_id"] = str(user.id)

#     return RedirectResponse(url="/wallet", status_code=303)