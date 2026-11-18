from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserResponse
from ..auth import get_current_user
from ..crud import get_users

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)) -> List[User]:
    """List sample users to allow switching context in the UI."""
    return get_users(db)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently selected user."""
    return current_user
