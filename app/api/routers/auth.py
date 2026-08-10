from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.dependencies import AuthServiceDep
from app.schemas.auth import AuthBase
from app.schemas.user import UserRead
from app.services.auth import UserAlreadyExistsError, WeakPasswordError

from app.db.redis_db import add_jti_to_blacklist
from app.schemas.dependencies import UserDep, get_access_token


router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="app/templates")


@router.post("/signup", response_model=UserRead)
def signup(credentials: AuthBase, currencies: list[str] | None, auth_service: AuthServiceDep):
    try:
        user = auth_service.create_user_with_wallets(credentials, currencies)

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

    return user


@router.post("/login")
def login(request_form: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthServiceDep):

    token = auth_service.authenticate_user(email=request_form.username, password=request_form.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    return {
        "access_token": token,
        "type": "jwt",
    }


@router.get("/logout")
def logout_user(token_data: Annotated[dict, Depends(get_access_token)],):
    add_jti_to_blacklist(token_data["jti"])
    return {
        "details": "Logged out"
    }

@router.get("/hello")
def hello_page(user: UserDep):
    return {"details": "hello"}

# @router.get("/signup", response_class=HTMLResponse)
# def signup_page(request: Request):
#     return templates.TemplateResponse(request=request, name="signup.html", context={})


# @router.get("/login", response_class=HTMLResponse)
# def login_page(request: Request):
#     error = request.session.pop("error", None)
#     return templates.TemplateResponse(
#         request=request,
#         name="login.html",
#         context={
#             "request": request,
#             "error": error,
#         },
#     )


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
