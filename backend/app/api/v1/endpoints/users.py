from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserUpdate
from app.api.v1.dependencies import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.sustainability_preferences is not None:
        current_user.sustainability_preferences = user_in.sustainability_preferences
    if user_in.preferred_materials is not None:
        current_user.preferred_materials = user_in.preferred_materials

    db.commit()
    db.refresh(current_user)
    return current_user
