from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas.dependencies import SignupDep, LoginDep, AuthServiceDep
from app.services.auth import UserAlreadyExistsError, WeakPasswordError


router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="app/templates")


@router.post("/signup")
def signup(request: Request, auth_service: AuthServiceDep, form: SignupDep):
    try:
        user = auth_service.create_user_with_wallets(
            email=form.email, password=form.password
        )

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        )

    request.session["user_id"] = str(user.id)
    return {"user_id": user.id}


@router.post("/login")
def login(request: Request, auth_service: AuthServiceDep, form: LoginDep):

    user = auth_service.authenticate_user(email=form.email, password=form.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Prevent Session Fixation: clear old session before setting new auth state
    request.session.clear()
    request.session["user_id"] = str(user.id)

    return {"user_id": user.id}


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return {
        "message": "Logged out"
    }


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html", context={})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    error = request.session.pop("error", None)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "error": error,
        },
    )


# Old version
# @router.post("/signup")
# def signup(
#     request: Request,
#     form: SignupSchema = Depends(SignupSchema.as_form),
#     db: DatabaseDep
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
