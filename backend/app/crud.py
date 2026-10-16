from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from . import models, schemas
from .auth import hash_password, is_support
from .models import Category, Status, Ticket, TicketComment, User

# Status lifecycle: open -> in_progress -> resolved -> closed (with reopen paths)
TRANSITIONS: dict[Status, set[Status]] = {
    Status.open: {Status.in_progress},
    Status.in_progress: {Status.resolved, Status.open},
    Status.resolved: {Status.closed, Status.in_progress},
    Status.closed: set(),
}


# ---------- Users ----------
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, data: schemas.UserCreate, force_role: models.Role | None = None) -> User:
    if get_user_by_email(db, data.email):
        raise HTTPException(400, "Email already registered")
    is_first = db.scalar(select(func.count(User.id))) == 0
    if force_role:
        role = force_role
    elif is_first:
        role = models.Role.admin
    elif data.role in (models.Role.student, models.Role.staff):
        role = data.role
    else:
        role = models.Role.student
    user = User(name=data.name, email=data.email.lower(), department=data.department,
                hashed_password=hash_password(data.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- Tickets ----------
def _ticket_query():
    return select(Ticket).options(selectinload(Ticket.creator), selectinload(Ticket.assignee))


def create_ticket(db: Session, data: schemas.TicketCreate, user: User) -> Ticket:
    ticket = Ticket(**data.model_dump(), created_by=user.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def filter_tickets(
    db: Session,
    user: User,
    *,
    status: Status | None = None,
    category: Category | None = None,
    priority: models.Priority | None = None,
    assigned_to: int | None = None,
    unassigned: bool = False,
    date_from: date | None = None,
    date_to: date | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Ticket]:
    stmt = _ticket_query()
    if not is_support(user):  # students/staff only see their own
        stmt = stmt.where(Ticket.created_by == user.id)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if category:
        stmt = stmt.where(Ticket.category == category)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if unassigned:
        stmt = stmt.where(Ticket.assigned_to.is_(None))
    elif assigned_to is not None:
        stmt = stmt.where(Ticket.assigned_to == assigned_to)
    if date_from:
        stmt = stmt.where(Ticket.created_at >= datetime.combine(date_from, time.min, timezone.utc))
    if date_to:
        stmt = stmt.where(Ticket.created_at < datetime.combine(date_to + timedelta(days=1), time.min, timezone.utc))
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Ticket.title.ilike(like), Ticket.description.ilike(like)))
    stmt = stmt.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_ticket(db: Session, ticket_id: int, user: User) -> Ticket:
    ticket = db.scalar(
        _ticket_query()
        .options(selectinload(Ticket.comments).selectinload(TicketComment.author))
        .where(Ticket.id == ticket_id)
    )
    if not ticket or (not is_support(user) and ticket.created_by != user.id):
        raise HTTPException(404, "Ticket not found")
    return ticket


def _log(db: Session, ticket: Ticket, actor: User, text: str) -> None:
    db.add(TicketComment(ticket_id=ticket.id, user_id=actor.id, comment=text, is_system=True))


def update_ticket(db: Session, ticket: Ticket, data: schemas.TicketUpdate, actor: User) -> Ticket:
    if ticket.status == Status.closed:
        raise HTTPException(400, "Closed tickets can't be changed")

    if data.status and data.status != ticket.status:
        if data.status not in TRANSITIONS[ticket.status]:
            raise HTTPException(400, f"Invalid status change: {ticket.status.value} -> {data.status.value}")
        _log(db, ticket, actor, f"Status changed from {ticket.status.value} to {data.status.value}")
        ticket.status = data.status
        if data.status == Status.resolved:
            ticket.resolved_at = datetime.now(timezone.utc)
        elif data.status in (Status.open, Status.in_progress):
            ticket.resolved_at = None

    if data.priority and data.priority != ticket.priority:
        _log(db, ticket, actor, f"Priority changed from {ticket.priority.value} to {data.priority.value}")
        ticket.priority = data.priority

    if data.unassign and ticket.assigned_to is not None:
        ticket.assigned_to = None
        _log(db, ticket, actor, "Ticket unassigned")
    elif data.assigned_to is not None and data.assigned_to != ticket.assigned_to:
        agent = db.get(User, data.assigned_to)
        if not agent or not is_support(agent):
            raise HTTPException(400, "Tickets can only be assigned to IT agents or admins")
        ticket.assigned_to = agent.id
        _log(db, ticket, actor, f"Assigned to {agent.name}")

    db.commit()
    db.expire_all()
    return get_ticket(db, ticket.id, actor)


def add_comment(db: Session, ticket: Ticket, user: User, text: str) -> TicketComment:
    c = TicketComment(ticket_id=ticket.id, user_id=user.id, comment=text)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ---------- Analytics ----------
def analytics(db: Session) -> schemas.Analytics:
    total = db.scalar(select(func.count(Ticket.id))) or 0
    by_status = dict(db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all())
    by_cat = dict(db.execute(select(Ticket.category, func.count()).group_by(Ticket.category)).all())
    resolved = db.execute(select(Ticket.created_at, Ticket.resolved_at).where(Ticket.resolved_at.is_not(None))).all()
    avg = (sum((r - c).total_seconds() for c, r in resolved) / len(resolved) / 3600) if resolved else None
    open_count = by_status.get(Status.open, 0) + by_status.get(Status.in_progress, 0)
    return schemas.Analytics(
        total=total,
        open_count=open_count,
        closed_count=total - open_count,
        avg_resolution_hours=round(avg, 2) if avg is not None else None,
        by_category=[schemas.CountItem(label=c.value, count=by_cat.get(c, 0)) for c in Category],
        by_status=[schemas.CountItem(label=s.value, count=by_status.get(s, 0)) for s in Status],
    )
