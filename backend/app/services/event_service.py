from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.event import Event
from app.models.registration import Registration
from app.models.volunteer import Volunteer
from app.models.feedback import Feedback
from app.schemas.event import EventResponse
from app.schemas.category import CategoryResponse
from app.schemas.user import UserResponse


def get_registered_count(db: Session, event_id: int) -> int:
    """Return count of active confirmed registrations for an event."""
    return (
        db.query(func.count(Registration.id))
        .filter(Registration.event_id == event_id, Registration.status == "Confirmed")
        .scalar()
        or 0
    )


def get_event_stats(db: Session, event_id: int):
    """Compute average rating and feedback count for an event."""
    res = (
        db.query(
            func.coalesce(func.avg(Feedback.rating), 0).label("avg_rating"),
            func.count(Feedback.id).label("cnt"),
        )
        .filter(Feedback.event_id == event_id)
        .first()
    )
    avg_rating = round(float(res.avg_rating), 1) if res and res.cnt > 0 else None
    feedback_cnt = res.cnt if res else 0
    return avg_rating, feedback_cnt


def enrich_event_response(
    db: Session,
    event: Event,
    current_user_id: Optional[int] = None,
) -> EventResponse:
    """Populate dynamic fields like registered_count, available_seats, and user statuses."""
    registered_cnt = get_registered_count(db, event.id)
    available_seats = max(0, event.capacity - registered_cnt)
    avg_rating, feedback_cnt = get_event_stats(db, event.id)

    is_registered = False
    is_volunteer = False
    vol_status = None

    if current_user_id:
        reg = (
            db.query(Registration)
            .filter(
                Registration.event_id == event.id,
                Registration.user_id == current_user_id,
                Registration.status == "Confirmed",
            )
            .first()
        )
        is_registered = reg is not None

        vol = (
            db.query(Volunteer)
            .filter(
                Volunteer.event_id == event.id,
                Volunteer.user_id == current_user_id,
            )
            .first()
        )
        if vol:
            is_volunteer = True
            vol_status = vol.status

    category_data = (
        CategoryResponse.model_validate(event.category) if event.category else None
    )
    organizer_data = (
        UserResponse.model_validate(event.organizer) if event.organizer else None
    )

    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        category_id=event.category_id,
        image_url=event.image_url,
        date=event.date,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        capacity=event.capacity,
        registration_deadline=event.registration_deadline,
        organizer_id=event.organizer_id,
        status=event.status,
        created_at=event.created_at,
        updated_at=event.updated_at,
        category=category_data,
        organizer=organizer_data,
        registered_count=registered_cnt,
        available_seats=available_seats,
        is_registered=is_registered,
        is_volunteer=is_volunteer,
        volunteer_status=vol_status,
        average_rating=avg_rating,
        feedback_count=feedback_cnt,
    )
