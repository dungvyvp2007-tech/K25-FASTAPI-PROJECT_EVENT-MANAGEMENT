from sqlalchemy.orm import Session

from models.activity_log import ActivityLog


def log_activity(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    description: str,
    event_id: int | None = None,
    task_id: int | None = None,
) -> ActivityLog:
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        event_id=event_id,
        task_id=task_id,
    )
    db.add(activity)
    return activity
