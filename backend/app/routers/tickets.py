from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Ticket
from ..schemas import (
    TicketCreate,
    TicketUpdate,
    TicketStatusUpdate,
    TicketResponse,
    TicketDetailResponse,
    normalize_category,
    normalize_priority,
    normalize_status,
)
from ..auth import get_current_user, require_support_role
from ..crud import (
    get_visible_tickets,
    get_ticket_by_id,
    create_ticket,
    update_ticket_content,
    update_ticket_status
)

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Ticket]:
    """
    List tickets.
    Employees see only their own tickets; support staff see all tickets.
    Supports multi-criteria filtering by status, category, and priority.
    """
    norm_status = None
    if status and status.upper() != "ALL":
        try:
            norm_status = normalize_status(status)
        except ValueError:
            norm_status = status

    norm_category = None
    if category and category.upper() != "ALL":
        try:
            norm_category = normalize_category(category)
        except ValueError:
            norm_category = category

    norm_priority = None
    if priority and priority.upper() != "ALL":
        try:
            norm_priority = normalize_priority(priority)
        except ValueError:
            norm_priority = priority

    return get_visible_tickets(
        db=db,
        user=current_user,
        status=norm_status,
        category=norm_category,
        priority=norm_priority
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Ticket:
    """
    Get a single ticket's details and comments.
    Employees can only view their own tickets.
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
            detail="Access denied. Employees can only view their own tickets."
        )

    return ticket


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def raise_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Ticket:
    """
    Raise a new IT support ticket.
    Rule: Only employees can create support tickets. Support staff are forbidden.
    Title (up to 100 characters) and description cannot be empty.
    """
    if current_user.role != "EMPLOYEE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can create support tickets."
        )

    return create_ticket(db, ticket_in, owner_id=current_user.id)


@router.put("/{ticket_id}", response_model=TicketResponse)
def edit_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Ticket:
    """
    Edit a ticket's title, description, category, or priority.
    Rule: Only the employee who created the ticket can edit its details while it is not Closed.
    Support staff cannot modify the employee's original ticket details.
    Closed tickets cannot be edited.
    """
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found."
        )

    # Permission check: Only the employee who created the ticket can edit it
    if current_user.role != "EMPLOYEE" or ticket.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the employee who created the ticket can edit its details."
        )

    # Rule: A Closed ticket cannot be edited
    if ticket.status == "Closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A Closed ticket cannot be edited."
        )

    try:
        updated = update_ticket_content(db, ticket, ticket_in)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    return updated


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def change_ticket_status(
    ticket_id: int,
    status_in: TicketStatusUpdate,
    support_user: User = Depends(require_support_role),
    db: Session = Depends(get_db)
) -> Ticket:
    """
    Change a ticket's status.
    Rule: Only support staff can change a ticket's status.
    Rule: Once a ticket is Closed, it cannot be reopened or edited.
    """
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found."
        )

    try:
        updated = update_ticket_status(db, ticket, status_in.status)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    return updated
