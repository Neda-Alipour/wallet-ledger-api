
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas.dependencies import signup_dependency, login_dependency, AuthServiceDependency


router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="app/templates")


@router.post("/signup")
def signup(
    request: Request,
    auth_service: AuthServiceDependency,
    form: signup_dependency
):

    user = auth_service.create_user_with_wallets(email=form.email, password=form.password)

    if user is None:
        request.session["error"] = "User already exists or an error occurred"
        return RedirectResponse(url="/signup", status_code=303)

    # 3. Finalize Session
    request.session["user_id"] = str(user.id)
    return RedirectResponse(url="/wallet", status_code=303)


@router.post("/login")
def login(
    request: Request,
    auth_service: AuthServiceDependency,
    form: login_dependency
):
    
    user = auth_service.authenticate_user(email=form.email, password=form.password)

    if not user:
        request.session["error"] = "Incorrect Initials"
        return RedirectResponse(url="/login", status_code=303)
    
    request.session["user_id"] = str(user.id)

    return RedirectResponse(url="/wallet", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="signup.html",
    context={}
)


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