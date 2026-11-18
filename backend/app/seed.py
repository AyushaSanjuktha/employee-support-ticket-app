from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .models import User, Ticket, Comment


def seed_sample_data(db: Session) -> None:
    """Seed the database with initial sample users and tickets if empty."""
    existing_users = db.query(User).first()
    if existing_users is not None:
        return

    # Create sample employees and support staff
    alice = User(name="Alice", email="alice@example.com", role="EMPLOYEE")
    bob = User(name="Bob", email="bob@example.com", role="EMPLOYEE")
    charlie = User(name="Charlie", email="charlie@example.com", role="SUPPORT")
    dana = User(name="Dana", email="dana@example.com", role="SUPPORT")

    db.add_all([alice, bob, charlie, dana])
    db.commit()

    base_time = datetime.now(timezone.utc)

    # 1. Laptop not charging | Hardware | High | Open | Owner: Alice
    t1 = Ticket(
        title="Laptop not charging",
        description="My work laptop stops charging when plugged into the dock or the wall adapter. Battery remains at 5%.",
        category="Hardware",
        priority="High",
        status="Open",
        owner_id=alice.id,
        created_at=base_time - timedelta(hours=4)
    )

    # 2. Cannot log in to VPN | Network | High | In Progress | Owner: Bob
    t2 = Ticket(
        title="Cannot log in to VPN",
        description="Getting authentication timeout error when attempting to connect to the corporate VPN from home.",
        category="Network",
        priority="High",
        status="In Progress",
        owner_id=bob.id,
        created_at=base_time - timedelta(hours=3)
    )

    # 3. Need access to the shared project folder | Access | Medium | Open | Owner: Alice
    t3 = Ticket(
        title="Need access to the shared project folder",
        description="Requesting read/write access to the engineering project folder for the Q4 rollout.",
        category="Access",
        priority="Medium",
        status="Open",
        owner_id=alice.id,
        created_at=base_time - timedelta(hours=2)
    )

    # 4. Excel keeps crashing on startup | Software | Medium | Resolved | Owner: Bob
    t4 = Ticket(
        title="Excel keeps crashing on startup",
        description="Excel crashes with an unexpected error code immediately after launching on Windows 11.",
        category="Software",
        priority="Medium",
        status="Resolved",
        owner_id=bob.id,
        created_at=base_time - timedelta(hours=1)
    )

    # 5. Request a second monitor | Hardware | Low | Closed | Owner: Alice
    t5 = Ticket(
        title="Request a second monitor",
        description="Need a secondary monitor for my workstation setup at desk 12B.",
        category="Hardware",
        priority="Low",
        status="Closed",
        owner_id=alice.id,
        created_at=base_time - timedelta(minutes=30)
    )

    db.add_all([t1, t2, t3, t4, t5])
    db.commit()

    # Seed comments demonstrating author name, timestamp, and comments on active and closed tickets
    c1 = Comment(
        ticket_id=t2.id,
        author_id=charlie.id,
        content="Looking into your VPN gateway route right now.",
        created_at=base_time - timedelta(hours=2, minutes=30)
    )
    c2 = Comment(
        ticket_id=t2.id,
        author_id=bob.id,
        content="Thanks Charlie, let me know if you need error logs.",
        created_at=base_time - timedelta(hours=2)
    )
    c3 = Comment(
        ticket_id=t4.id,
        author_id=dana.id,
        content="Cleared the Office add-in cache and restarted Excel in safe mode. Issue resolved.",
        created_at=base_time - timedelta(minutes=45)
    )
    c4 = Comment(
        ticket_id=t5.id,
        author_id=charlie.id,
        content="Monitor delivered and set up at desk 12B. Closing ticket.",
        created_at=base_time - timedelta(minutes=20)
    )
    c5 = Comment(
        ticket_id=t5.id,
        author_id=alice.id,
        content="Thank you, working great!",
        created_at=base_time - timedelta(minutes=10)
    )

    db.add_all([c1, c2, c3, c4, c5])
    db.commit()
