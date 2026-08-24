from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from db.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    event_id = Column(ForeignKey("events.id", ondelete="SET NULL"), index=True)
    task_id = Column(ForeignKey("event_tasks.id", ondelete="SET NULL"), index=True)
    user_id = Column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
