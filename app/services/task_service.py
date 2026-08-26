from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.config import settings
from dependencies.permissions import ensure_member, ensure_owner, get_event_or_404
from models.event import EventStaff
from models.event_task import Attachment, Comment, EventTask
from models.user import User
from schemas.task import CommentCreate, TaskCreate, TaskUpdate
from services.activity_logs import log_activity

VALID_STATUS = {"TODO", "IN_PROGRESS", "DONE"}
VALID_PRIORITY = {"LOW", "MEDIUM", "HIGH"}


def get_task_or_404(db: Session, task_id: int) -> EventTask:
    task = db.get(EventTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy công việc")
    return task


def _ensure_assignee_is_member(
    db: Session, event_id: int, assignee_id: int | None
) -> None:
    event = get_event_or_404(db, event_id)
    assignee = db.get(User, assignee_id) if assignee_id is not None else None
    if assignee is not None and not assignee.is_active:
        raise HTTPException(
            status_code=422,
            detail="Không thể giao công việc cho tài khoản đã bị khóa",
        )
    if (
        assignee_id is not None
        and assignee_id != event.owner_id
        and not db.get(EventStaff, (event_id, assignee_id))
    ):
        raise HTTPException(
            status_code=422, detail="Người được giao phải là thành viên của sự kiện"
        )


def create_task(
    db: Session, event_id: int, payload: TaskCreate, user: User
) -> EventTask:
    event = get_event_or_404(db, event_id)
    ensure_member(db, event, user)
    if payload.priority not in VALID_PRIORITY:
        raise HTTPException(
            status_code=422, detail="Độ ưu tiên phải là LOW, MEDIUM hoặc HIGH"
        )
    if payload.status not in VALID_STATUS:
        raise HTTPException(
            status_code=422, detail="Trạng thái phải là TODO,IN_PROGRESS hoặc DONE"
        )
    _ensure_assignee_is_member(db, event_id, payload.assignee_id)       
    task = EventTask(**payload.model_dump(), event_id=event_id)
    db.add(task)
    db.flush()
    log_activity(
        db,
        user_id=user.id,
        event_id=event_id,
        task_id=task.id,
        action="TASK_CREATED",
        description=f"Đã tạo công việc: {task.title}",
    )
    db.commit()
    db.refresh(task)
    return task


def get_tasks(
    db: Session,
    event_id: int,
    user: User,
    status_filter: str | None = None,
    assignee_id: int | None = None,
    priority: str | None = None,
    page: int = 1,
    page_size: int = 3,
) -> list[EventTask]:
    event = get_event_or_404(db, event_id)
    ensure_member(db, event, user)
    tasks_query = db.query(EventTask).filter(EventTask.event_id == event_id)
    if status_filter:
        tasks_query = tasks_query.filter(EventTask.status == status_filter)
    if assignee_id:
        tasks_query = tasks_query.filter(EventTask.assignee_id == assignee_id)
    if priority:
        tasks_query = tasks_query.filter(EventTask.priority == priority)
    offset_value = (page - 1) * page_size
    tasks_query = (
        tasks_query.order_by(EventTask.due_date.is_(None), EventTask.due_date)
        .offset(offset_value)
        .limit(page_size)
    )

    return tasks_query.all()


def get_task_detail(db: Session, task_id: int, user: User) -> EventTask:
    task = get_task_or_404(db, task_id)
    ensure_member(db, get_event_or_404(db, task.event_id), user)
    return task


def update_task(
    db: Session, task_id: int, payload: TaskUpdate, user: User
) -> EventTask:
    task = get_task_or_404(db, task_id)
    event = get_event_or_404(db, task.event_id)
    ensure_member(db, event, user)
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and changes["status"] not in VALID_STATUS:
        raise HTTPException(
            status_code=422, detail="Trạng thái phải là TODO, IN_PROGRESS hoặc DONE"
        )
    if "priority" in changes and changes["priority"] not in VALID_PRIORITY:
        raise HTTPException(
            status_code=422, detail="Độ ưu tiên phải là LOW, MEDIUM hoặc HIGH"
        )
    if "assignee_id" in changes:
        _ensure_assignee_is_member(db, task.event_id, changes["assignee_id"])
    protected_fields = {"title", "description", "assignee_id", "priority", "due_date"}
    if protected_fields.intersection(changes) and user.id != task.assignee_id:
        ensure_owner(db, event, user)
    for key, value in changes.items():
        setattr(task, key, value)
    if changes:
        log_activity(
            db,
            user_id=user.id,
            event_id=task.event_id,
            task_id=task.id,
            action="TASK_UPDATED",
            description=f"Đã cập nhật công việc: {task.title}",
        )
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user: User) -> dict:
    task = get_task_or_404(db, task_id)
    event = get_event_or_404(db, task.event_id)
    ensure_owner(db, event, user)
    log_activity(
        db,
        user_id=user.id,
        event_id=task.event_id,
        task_id=task.id,
        action="TASK_DELETED",
        description=f"Đã xóa công việc: {task.title}",
    )
    db.delete(task)
    db.commit()
    return {"message": "Đã xóa công việc thành công"}


def add_comment(db: Session, task_id: int, payload: CommentCreate, user: User) -> dict:
    task = get_task_or_404(db, task_id)
    ensure_member(db, get_event_or_404(db, task.event_id), user)
    db.add(Comment(task_id=task_id, user_id=user.id, content=payload.content))
    log_activity(
        db,
        user_id=user.id,
        event_id=task.event_id,
        task_id=task.id,
        action="TASK_COMMENT_ADDED",
        description=f"Đã thêm bình luận vào công việc: {task.title}",
    )
    db.commit()
    return {"message": "Đã thêm bình luận"}


def get_comments(db: Session, task_id: int, user: User) -> list[Comment]:
    task = get_task_or_404(db, task_id)
    ensure_member(db, get_event_or_404(db, task.event_id), user)
    return (
        db.query(Comment)
        .filter(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


def add_attachment(db: Session, task_id: int, file: UploadFile, user: User) -> dict:
    task = get_task_or_404(db, task_id)
    ensure_member(db, get_event_or_404(db, task.event_id), user)
    safe_name = f"{uuid4().hex}_{Path(file.filename or 'tep').name}"
    destination = Path(settings.upload_dir) / safe_name
    with destination.open("wb") as output:
        while chunk := file.file.read(1024 * 1024):
            output.write(chunk)
    db.add(
        Attachment(
            task_id=task_id,
            user_id=user.id,
            file_name=file.filename or safe_name,
            file_path=str(destination),
        )
    )
    log_activity(
        db,
        user_id=user.id,
        event_id=task.event_id,
        task_id=task.id,
        action="TASK_ATTACHMENT_UPLOADED",
        description=f"Đã tải tệp đính kèm lên công việc: {task.title}",
    )
    db.commit()
    return {"message": "Tải tệp đính kèm lên thành công"}
