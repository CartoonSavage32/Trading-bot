from fastapi import APIRouter
from app.api.v1.endpoints import trading, auth

api_router = APIRouter()
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
