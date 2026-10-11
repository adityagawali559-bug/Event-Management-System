from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AnnouncementCreate(BaseModel):
    message: str = Field(..., min_length=2)


class AnnouncementResponse(BaseModel):
    id: int
    event_id: int
    organizer_id: int
    message: str
    created_at: datetime

    organizer_name: Optional[str] = None
    event_title: Optional[str] = None

    class Config:
        from_attributes = True
