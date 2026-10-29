from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse


class RegistrationCreate(BaseModel):
    event_id: int


class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: datetime
    status: str

    user: Optional[UserResponse] = None
    event_title: Optional[str] = None
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    event_status: Optional[str] = None
    event_image_url: Optional[str] = None

    class Config:
        from_attributes = True
