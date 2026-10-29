from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List
from datetime import date as DateType, time as TimeType, datetime
from app.schemas.category import CategoryResponse
from app.schemas.user import UserResponse


EventStatusLiteral = Literal[
    "Draft",
    "Pending Approval",
    "Approved",
    "Rejected",
    "Published",
    "Completed",
    "Cancelled",
]


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    image_url: Optional[str] = None
    date: DateType
    start_time: TimeType
    end_time: TimeType
    location: str = Field(..., min_length=2, max_length=255)
    capacity: int = Field(..., ge=1)
    registration_deadline: datetime
    status: Optional[EventStatusLiteral] = "Draft"

    @field_validator("capacity")
    def validate_capacity(cls, v):
        if v < 1:
            raise ValueError("Capacity must be at least 1.")
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    date: Optional[DateType] = None
    start_time: Optional[TimeType] = None
    end_time: Optional[TimeType] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    capacity: Optional[int] = Field(None, ge=1)
    registration_deadline: Optional[datetime] = None
    status: Optional[EventStatusLiteral] = None


class EventResponse(EventBase):
    id: int
    category_id: int
    organizer_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    category: Optional[CategoryResponse] = None
    organizer: Optional[UserResponse] = None

    registered_count: int = 0
    available_seats: int = 0
    is_registered: bool = False
    is_volunteer: bool = False
    volunteer_status: Optional[str] = None
    average_rating: Optional[float] = None
    feedback_count: int = 0

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    size: int
    pages: int
