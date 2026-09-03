from fastapi import APIRouter, Depends, status ,Query
from typing import Optional
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.activity import ActivityLogOut
from schemas.common import MessageResponse
from schemas.event import EventCreate, EventOut, EventUpdate, MemberCreate, MemberOut
from services import event_service

router = APIRouter(prefix="/events")


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED, tags=["Event"])
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return event_service.create_event(db, payload, user)


@router.get("", response_model=list[EventOut], tags=["Event"])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user),search: Optional[str] = Query(None, description="Tìm kiếm theo tên event")):
    return event_service.get_events(db, user,search)


@router.get("/{event_id}", response_model=EventOut, tags=["Event"])
def detail_event(
    event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return event_service.get_event_detail(db, event_id, user)


@router.patch("/{event_id}", response_model=EventOut, tags=["Event"])
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return event_service.update_event(db, event_id, payload, user)


@router.delete("/{event_id}", response_model=MessageResponse, tags=["Event"])
def delete_event(
    event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return event_service.delete_event(db, event_id, user)


@router.post(
    "/{event_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED, tags=["Event Staff"]
)
def add_member(
    event_id: int,
    payload: MemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return event_service.add_event_member(db, event_id, payload, user)


@router.get("/{event_id}/members", response_model=list[MemberOut],tags=["Event Staff"])
def list_members(
    event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return event_service.get_event_members(db, event_id, user)


@router.get("/{event_id}/activity-logs", response_model=list[ActivityLogOut],tags=["Event Staff"])
def list_activity_logs(
    event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return event_service.get_activity_logs(db, event_id, user)


@router.delete("/{event_id}/members/{user_id}", response_model=MessageResponse,tags=["Event Staff"])
def remove_member(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return event_service.remove_event_member(db, event_id, user_id, user)
