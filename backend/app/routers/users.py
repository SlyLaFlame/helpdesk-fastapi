from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import SUPPORT_ROLES, get_current_user, require_roles
from ..database import get_db
from ..models import Role, User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/agents", response_model=list[schemas.UserBrief])
def agents(db: Session = Depends(get_db), _: User = Depends(require_roles(*SUPPORT_ROLES))):
    return db.scalars(select(User).where(User.role.in_(SUPPORT_ROLES)).order_by(User.name)).all()


@router.get("", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.admin))):
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/{user_id}/role", response_model=schemas.UserOut)
def set_role(
    user_id: int, data: schemas.RoleUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles(Role.admin))
):
    if user_id == admin.id:
        raise HTTPException(400, "You can't change your own role")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.role = data.role
    db.commit()
    db.refresh(user)
    return user
