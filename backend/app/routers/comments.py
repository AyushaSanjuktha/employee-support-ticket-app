from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import CommentCreate, CommentResponse
from ..auth import get_current_user
from ..crud import get_ticket_by_id, create_comment, get_ticket_comments

router = APIRouter(prefix="/api/tickets", tags=["comments"])


@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def list_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[CommentResponse]:
    """Retrieve comments for a specific ticket."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found."
        )

    if current_user.role != "SUPPORT" and ticket.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Employees can only view comments on their own tickets."
        )

    return get_ticket_comments(db, ticket_id)


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def post_comment(
    ticket_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CommentResponse:
    """
    Add a comment to a ticket.
    Rule: A Closed ticket cannot be edited, but comments can still be added.
    """
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found."
        )

    if current_user.role != "SUPPORT" and ticket.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Employees can only comment on their own tickets."
        )

    # Note: comments are allowed even if ticket is CLOSED as per rule!
    return create_comment(
        db=db,
        ticket_id=ticket_id,
        author_id=current_user.id,
        content=comment_in.content
    )
