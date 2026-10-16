from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import SUPPORT_ROLES, get_current_user, is_support, require_roles
from ..database import get_db
from ..models import Category, Priority, Status, User

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=schemas.TicketOut, status_code=201)
def create_ticket(data: schemas.TicketCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.create_ticket(db, data, user)


@router.get("", response_model=list[schemas.TicketOut])
def list_tickets(
    status: Status | None = None,
    category: Category | None = None,
    priority: Priority | None = None,
    assigned_to: int | None = None,
    unassigned: bool = False,
    date_from: date | None = None,
    date_to: date | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud.filter_tickets(
        db, user, status=status, category=category, priority=priority, assigned_to=assigned_to,
        unassigned=unassigned, date_from=date_from, date_to=date_to, q=q, skip=skip, limit=min(limit, 500),
    )


@router.get("/analytics", response_model=schemas.Analytics)
def analytics(db: Session = Depends(get_db), _: User = Depends(require_roles(*SUPPORT_ROLES))):
    return crud.analytics(db)


@router.get("/{ticket_id}", response_model=schemas.TicketDetail)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.get_ticket(db, ticket_id, user)


@router.patch("/{ticket_id}", response_model=schemas.TicketDetail)
def update_ticket(
    ticket_id: int,
    data: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*SUPPORT_ROLES)),
):
    ticket = crud.get_ticket(db, ticket_id, user)
    return crud.update_ticket(db, ticket, data, user)


@router.post("/{ticket_id}/comments", response_model=schemas.CommentOut, status_code=201)
def add_comment(
    ticket_id: int, data: schemas.CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    ticket = crud.get_ticket(db, ticket_id, user)
    if ticket.status == Status.closed and not is_support(user):
        raise HTTPException(400, "Ticket is closed")
    return crud.add_comment(db, ticket, user, data.comment)
