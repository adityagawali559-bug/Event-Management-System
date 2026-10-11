from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from app.schemas.user import UserResponse

VolunteerStatusLiteral = Literal["Pending", "Approved", "Rejected", "Completed"]


class VolunteerCreate(BaseModel):
    event_id: int


class VolunteerUpdate(BaseModel):
    status: VolunteerStatusLiteral


class VolunteerResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    applied_at: datetime
    updated_at: datetime

    user: Optional[UserResponse] = None
    event_title: Optional[str] = None
    event_date: Optional[str] = None
    event_location: Optional[str] = None

    class Config:
        from_attributes = True
