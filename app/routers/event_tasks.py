from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.common import MessageResponse
from schemas.task import CommentCreate, CommentOut, TaskCreate, TaskOut, TaskUpdate
from services import task_service

router = APIRouter(tags=["Event Task"])


@router.post(
    "/events/{event_id}/event-tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    event_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.create_task(db, event_id, payload, user)


@router.get("/events/{event_id}/event-tasks", response_model=list[TaskOut])
def list_tasks(
    event_id: int,
    status_filter: str | None = Query(None, alias="status"),
    assignee_id: int | None = None,
    priority: str | None = None,
    page: int = Query(default=1, ge=1, description="Số trang hiện tại (bắt đầu từ 1)"),
    page_size: int = Query(default=3, ge=1, le=100, description="Số lượng phần tử trên mỗi trang"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.get_tasks(
        db, event_id, user, status_filter, assignee_id, priority,page,page_size
    )


@router.get("/event-tasks/{task_id}", response_model=TaskOut)
def task_detail(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return task_service.get_task_detail(db, task_id, user)


@router.patch("/event-tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.update_task(db, task_id, payload, user)


@router.delete("/event-tasks/{task_id}", response_model=MessageResponse)
def delete_task(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return task_service.delete_task(db, task_id, user)


@router.post(
    "/event-tasks/{task_id}/comments",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.add_comment(db, task_id, payload, user)


@router.get("/event-tasks/{task_id}/comments", response_model=list[CommentOut])
def list_comments(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return task_service.get_comments(db, task_id, user)


@router.post(
    "/event-tasks/{task_id}/attachments",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return task_service.add_attachment(db, task_id, file, user)
