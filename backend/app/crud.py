from typing import List, Optional
from sqlalchemy.orm import Session
from .models import User, Ticket, Comment
from .schemas import TicketCreate, TicketUpdate, UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by their email address."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session) -> List[User]:
    """List all registered users."""
    return db.query(User).order_by(User.id.asc()).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user record."""
    user = User(
        name=user_in.name,
        email=user_in.email,
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_visible_tickets(
    db: Session,
    user: User,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None
) -> List[Ticket]:
    """
    Return tickets visible to the given user based on their role,
    with support for multi-criteria filtering and newest-first sorting.
    """
    query = db.query(Ticket)

    # An employee sees only their own tickets; support staff see all
    if user.role != "SUPPORT":
        query = query.filter(Ticket.owner_id == user.id)

    # Optional multi-filter criteria
    if status and status != "ALL":
        query = query.filter(Ticket.status == status)
    if category and category != "ALL":
        query = query.filter(Ticket.category == category)
    if priority and priority != "ALL":
        query = query.filter(Ticket.priority == priority)

    # Default sorting: Newest tickets first
    return query.order_by(Ticket.created_at.desc()).all()


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    """Fetch a single ticket by its primary key ID."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def create_ticket(db: Session, ticket_in: TicketCreate, owner_id: int) -> Ticket:
    """Create a new ticket assigned to the specified owner."""
    ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        category=ticket_in.category,
        priority=ticket_in.priority,
        status="Open",
        owner_id=owner_id
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_content(db: Session, ticket: Ticket, update_in: TicketUpdate) -> Ticket:
    """Update editable fields of an active ticket."""
    if ticket.status == "Closed":
        raise ValueError("A Closed ticket cannot be edited.")

    if update_in.title is not None:
        ticket.title = update_in.title
    if update_in.description is not None:
        ticket.description = update_in.description
    if update_in.category is not None:
        ticket.category = update_in.category
    if update_in.priority is not None:
        ticket.priority = update_in.priority

    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket: Ticket, new_status: str) -> Ticket:
    """
    Update ticket status.
    Rule: Once a ticket is Closed, it cannot be reopened or edited.
    """
    if ticket.status == "Closed":
        raise ValueError("Once a ticket is Closed, it cannot be reopened or edited.")

    ticket.status = new_status
    db.commit()
    db.refresh(ticket)
    return ticket


def create_comment(db: Session, ticket_id: int, author_id: int, content: str) -> Comment:
    """Add a new comment to a ticket. Allowed even if the ticket is closed."""
    comment = Comment(
        ticket_id=ticket_id,
        author_id=author_id,
        content=content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_ticket_comments(db: Session, ticket_id: int) -> List[Comment]:
    """Retrieve all comments belonging to a ticket ordered chronologically."""
    return db.query(Comment).filter(Comment.ticket_id == ticket_id).order_by(Comment.created_at.asc()).all()
