from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_user, require_admin
from models.user import User
from schemas.user import UserOut
from services import user_service

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return user_service.get_my_profile(current_user)


@router.get("", response_model=list[UserOut])
def list_users(
    q: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.get_users(db, q)
