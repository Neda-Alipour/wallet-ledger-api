from fastapi import APIRouter

from app.api.routers import auth, wallet

master_router = APIRouter()

master_router.include_router(auth.router)
master_router.include_router(wallet.router)