from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int | None
    task_id: int | None
    user_id: int | None
    action: str
    description: str
    created_at: datetime
