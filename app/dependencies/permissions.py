from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.event import Event, EventStaff
from models.user import User


def get_event_or_404(db: Session, event_id: int) -> Event:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Không tìm thấy sự kiện")
    return event


def ensure_member(db: Session, event: Event, user: User) -> None:
    if user.role == "ADMIN" or event.owner_id == user.id:
        return

    if not db.get(EventStaff, (event.id, user.id)):
        raise HTTPException(
            status_code=403, detail="Bạn không phải thành viên của sự kiện này"
        )


def ensure_owner(db: Session, event: Event, user: User) -> None:
    if user.role != "ADMIN" and event.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Chỉ chủ sự kiện hoặc quản trị viên mới có quyền thực hiện thao tác này",
        )
