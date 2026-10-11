from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.feedback import Feedback
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["Feedback"])


@router.post("/events/{event_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    event_id: int,
    fb_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit rating and review for an event.
    Participant must have registered for the event.
    Only one feedback entry is permitted per user per event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    # Check registration
    reg = (
        db.query(Registration)
        .filter(Registration.event_id == event_id, Registration.user_id == current_user.id)
        .first()
    )
    if not reg or reg.status != "Confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must have a confirmed registration to submit feedback for this event.",
        )

    # Check for existing feedback
    existing = (
        db.query(Feedback)
        .filter(Feedback.event_id == event_id, Feedback.user_id == current_user.id)
        .first()
    )
    if existing:
        # Update existing feedback
        existing.rating = fb_in.rating
        existing.comment = fb_in.comment.strip() if fb_in.comment else None
        db.commit()
        db.refresh(existing)
        return build_fb_response(existing, current_user.full_name, event.title)

    # Insert new feedback
    new_fb = Feedback(
        user_id=current_user.id,
        event_id=event.id,
        rating=fb_in.rating,
        comment=fb_in.comment.strip() if fb_in.comment else None,
    )
    db.add(new_fb)
    db.commit()
    db.refresh(new_fb)

    return build_fb_response(new_fb, current_user.full_name, event.title)


@router.get("/events/{event_id}/feedback", response_model=List[FeedbackResponse])
def get_event_feedbacks(
    event_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all feedback reviews submitted for an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.event_id == event_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    res = []
    for fb in feedbacks:
        user_name = fb.user.full_name if fb.user else "Anonymous User"
        res.append(build_fb_response(fb, user_name, event.title))
    return res


def build_fb_response(fb: Feedback, user_name: str, event_title: str) -> FeedbackResponse:
    return FeedbackResponse(
        id=fb.id,
        user_id=fb.user_id,
        event_id=fb.event_id,
        rating=fb.rating,
        comment=fb.comment,
        created_at=fb.created_at,
        updated_at=fb.updated_at,
        user_name=user_name,
        event_title=event_title,
    )
