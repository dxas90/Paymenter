from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_active_user
from app.models.models import User
from app.schemas.schemas import User as UserSchema

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user
