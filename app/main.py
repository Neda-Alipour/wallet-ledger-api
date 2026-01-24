from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import ValidationError

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.wallet import router as wallet_router

app = FastAPI(title="Wallet Ledger API", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    referer = request.headers.get("referer", "/login")
    return RedirectResponse(
        url=referer + "?error=Invalid input",
        status_code=303
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    referer = request.headers.get("referer", "/login")

    # extract first error message nicely
    error_msg = exc.errors()[0]["msg"]

    return RedirectResponse(
        url=referer + f"?error={error_msg}",
        status_code=303
    )

app.include_router(auth_router, tags=["auth"])
app.include_router(wallet_router, tags=["wallet"])

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=1800,  # 30 minutes
    same_site="lax",
    https_only=False # True in production
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

def require_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user_id

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Why this happens (important concept)

# There are two types of validation errors in FastAPI:

# 1️⃣ RequestValidationError

# Happens when FastAPI validates request body/query/path automatically.

# 2️⃣ Pydantic ValidationError

# Happens when you manually create a schema:

# cls(email=email, password=password)


# You must handle both.

# This is a very real-world bug — many juniors hit this exact issue.