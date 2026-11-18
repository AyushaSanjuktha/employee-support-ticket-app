from typing import Optional
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import User


def get_current_user(
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db)
) -> User:
    """Resolve current user based on the X-User-Email header."""
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide X-User-Email header."
        )

    user = db.query(User).filter(User.email == x_user_email.strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with email '{x_user_email}' not found."
        )
    return user


def require_support_role(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the authenticated user has SUPPORT role."""
    if current_user.role != "SUPPORT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only support staff can perform this action."
        )
    return current_user
