from fastapi import APIRouter, Depends, HTTPException
from app.api.models.user import User
from app.api.services.user_service import UserService

router = APIRouter()


@router.post("/token")
def login(user: User, user_service: UserService = Depends()):
    user_in_db = user_service.authenticate_user(user)
    if not user_in_db:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": user_in_db.username, "token_type": "bearer"}
