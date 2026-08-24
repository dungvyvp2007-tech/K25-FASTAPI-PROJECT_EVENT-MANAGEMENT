from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime


class MemberCreate(BaseModel):
    user_id: int


class MemberOut(BaseModel):
    event_id: int
    user_id: int
    role: str
    joined_at: datetime
