from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas.auth import SignupSchema, LoginSchema
from app.db.session import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.services.auth import hash_password, verify_password

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
def signup(
    request: Request,
    form: SignupSchema = Depends(SignupSchema.as_form),
    db: Session = Depends(get_db)
):
    # Use 'with db.begin_nested()' if a transaction has already started
    # OR just use the session directly since it handles the transaction
        
    try:
        # 1. Start the atomic block immediately
        with db.begin_nested():
            # Check for existing user INSIDE the transaction for safety
            existing = db.query(User).filter(User.email == form.email).first()
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
def login(
    request: Request,
    form: LoginSchema = Depends(LoginSchema.as_form),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form.email).first()

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
#     db: Session = Depends(get_db)
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