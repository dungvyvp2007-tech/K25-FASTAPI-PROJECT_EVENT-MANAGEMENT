from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.permissions import ensure_member, ensure_owner, get_event_or_404
from models.activity_log import ActivityLog
from models.event import Event, EventStaff
from models.user import User
from schemas.event import EventCreate, EventUpdate, MemberCreate
from services.activity_logs import log_activity


def create_event(db: Session, payload: EventCreate, user: User) -> Event:
    event = Event(**payload.model_dump(), owner_id=user.id)
    db.add(event)
    db.flush()
    log_activity(
        db,
        user_id=user.id,
        event_id=event.id,
        action="EVENT_CREATED",
        description=f"Đã tạo sự kiện: {event.name}",
    )
    db.commit()
    db.refresh(event)
    return event


def get_events(db: Session, user: User, search: Optional[str] = None):
    if user.role == "ADMIN":
        events_query = db.query(Event)
    else:
        events_query = (
            db.query(Event)
            .outerjoin(EventStaff)
            .filter(or_(Event.owner_id == user.id, EventStaff.user_id == user.id))
        )
    if search and search.strip():
        search_pattern = f"%{search.strip()}%"
        events_query = events_query.filter(Event.name.ilike(search_pattern))

    return events_query.order_by(Event.created_at.desc()).distinct().all()


def get_event_detail(db: Session, event_id: int, user: User) -> Event:
    event = get_event_or_404(db, event_id)
    ensure_member(db, event, user)
    return event


def update_event(db: Session, event_id: int, payload: EventUpdate, user: User) -> Event:
    event = get_event_or_404(db, event_id)
    ensure_owner(db, event, user)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(event, key, value)
    if changes:
        log_activity(
            db,
            user_id=user.id,
            event_id=event.id,
            action="EVENT_UPDATED",
            description=f"Đã cập nhật sự kiện: {event.name}",
        )
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event_id: int, user: User) -> dict:
    event = get_event_or_404(db, event_id)
    ensure_owner(db, event, user)
    log_activity(
        db,
        user_id=user.id,
        event_id=event.id,
        action="EVENT_DELETED",
        description=f"Đã xóa sự kiện: {event.name}",
    )
    db.delete(event)
    db.commit()
    return {"message": "Đã xóa sự kiện thành công"}


def add_event_member(
    db: Session, event_id: int, payload: MemberCreate, user: User
) -> EventStaff:
    event = get_event_or_404(db, event_id)
    ensure_owner(db, event, user)
    member_user = db.get(User, payload.user_id)
    if not member_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    if not member_user.is_active:
        raise HTTPException(
            status_code=422,
            detail="Không thể thêm tài khoản đã bị khóa vào sự kiện",
        )
    if payload.user_id == event.owner_id or db.get(
        EventStaff, (event_id, payload.user_id)
    ):
        raise HTTPException(
            status_code=409, detail="Người dùng đã là thành viên sự kiện"
        )
    member = EventStaff(event_id=event_id, user_id=payload.user_id)
    db.add(member)
    log_activity(
        db,
        user_id=user.id,
        event_id=event_id,
        action="EVENT_MEMBER_ADDED",
        description=f"Đã thêm người dùng #{payload.user_id} vào sự kiện",
    )
    db.commit()
    db.refresh(member)
    return member


def get_event_members(db: Session, event_id: int, user: User) -> list[EventStaff]:
    event = get_event_or_404(db, event_id)
    ensure_member(db, event, user)
    return db.query(EventStaff).filter(EventStaff.event_id == event_id).all()


def get_activity_logs(db: Session, event_id: int, user: User) -> list[ActivityLog]:
    event = get_event_or_404(db, event_id)
    ensure_member(db, event, user)
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.event_id == event_id)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )


def remove_event_member(db: Session, event_id: int, user_id: int, user: User) -> dict:
    event = get_event_or_404(db, event_id)
    ensure_owner(db, event, user)
    member = db.get(EventStaff, (event_id, user_id))
    if not member:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy thành viên trong sự kiện"
        )
    if member.role == "OWNER":
        owner_count = (
            db.query(EventStaff)
            .filter(
                EventStaff.event_id == event_id,
                EventStaff.role == "OWNER",
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Không thể xóa owner cuối cùng của sự kiện",
            )
    log_activity(
        db,
        user_id=user.id,
        event_id=event_id,
        action="EVENT_MEMBER_REMOVED",
        description=f"Đã xóa người dùng #{user_id} khỏi sự kiện",
    )
    db.delete(member)
    db.commit()
    return {"message": "Đã xóa thành viên khỏi sự kiện"}
