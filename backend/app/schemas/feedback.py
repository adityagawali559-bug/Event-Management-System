from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    user_name: Optional[str] = None
    event_title: Optional[str] = None

    class Config:
        from_attributes = True
