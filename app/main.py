from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import ValidationError
from scalar_fastapi import get_scalar_api_reference

from app.core.config import db_settings
from app.api.router import master_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Wallet Ledger API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# templates = Jinja2Templates(directory="app/templates")

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = exc.errors()[0]["msg"]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,  # HTTP 422
        content={"detail": error_msg},
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):

    # extract first error message nicely
    error_msg = exc.errors()[0]["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,  # HTTP 422
        content={"detail": error_msg},
    )

app.include_router(master_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=db_settings.SECRET_KEY,
    max_age=1800,  # 30 minutes
    same_site="lax",
    https_only=False # True in production
)

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )

# Why this happens (important concept)

# There are two types of validation errors in FastAPI:

# 1️⃣ RequestValidationError

# Happens when FastAPI validates request body/query/path automatically.

# 2️⃣ Pydantic ValidationError

# Happens when you manually create a schema:

# cls(email=email, password=password)


# You must handle both.

# This is a very real-world bug — many juniors hit this exact issue.