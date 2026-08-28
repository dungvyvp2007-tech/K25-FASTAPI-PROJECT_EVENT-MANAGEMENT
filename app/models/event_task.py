from datetime import datetime,timedelta
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from db.database import Base


class EventTask(Base):

    __tablename__ = "event_tasks"
    id = Column(Integer, primary_key=True)
    event_id = Column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assignee_id = Column(ForeignKey("users.id", ondelete="SET NULL"))
    status = Column(String(20), default="TODO", nullable=False)
    priority = Column(String(20), default="MEDIUM", nullable=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Comment(Base):

    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    task_id = Column(ForeignKey("event_tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Attachment(Base):

    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    task_id = Column(ForeignKey("event_tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
