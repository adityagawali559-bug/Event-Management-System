from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.user import User
from app.models.registration import Registration
from app.models.volunteer import Volunteer
from app.models.notification import Notification
from app.models.event import Event
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_password_hash
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update profile information for the authenticated user."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name.strip()
    if user_update.mobile is not None:
        current_user.mobile = user_update.mobile.strip()
    if user_update.password is not None and len(user_update.password) >= 6:
        current_user.password_hash = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/dashboard-stats")
def get_user_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive dashboard stats tailored to the current user's role."""
    now = func.now()

    # Participant statistics
    total_registered = (
        db.query(func.count(Registration.id))
        .filter(Registration.user_id == current_user.id, Registration.status == "Confirmed")
        .scalar()
        or 0
    )

    upcoming_count = (
        db.query(func.count(Registration.id))
        .join(Event, Registration.event_id == Event.id)
        .filter(
            Registration.user_id == current_user.id,
            Registration.status == "Confirmed",
            Event.date >= func.current_date(),
        )
        .scalar()
        or 0
    )

    completed_count = (
        db.query(func.count(Registration.id))
        .join(Event, Registration.event_id == Event.id)
        .filter(
            Registration.user_id == current_user.id,
            Registration.status == "Confirmed",
            Event.date < func.current_date(),
        )
        .scalar()
        or 0
    )

    volunteer_count = (
        db.query(func.count(Volunteer.id))
        .filter(Volunteer.user_id == current_user.id)
        .scalar()
        or 0
    )

    unread_notifications = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .scalar()
        or 0
    )

    # Organizer statistics if applicable
    organizer_stats = None
    if current_user.role in ["organizer", "admin"]:
        total_created = (
            db.query(func.count(Event.id))
            .filter(Event.organizer_id == current_user.id)
            .scalar()
            or 0
        )
        org_upcoming = (
            db.query(func.count(Event.id))
            .filter(Event.organizer_id == current_user.id, Event.date >= func.current_date())
            .scalar()
            or 0
        )
        org_completed = (
            db.query(func.count(Event.id))
            .filter(Event.organizer_id == current_user.id, Event.date < func.current_date())
            .scalar()
            or 0
        )
        total_attendees = (
            db.query(func.count(Registration.id))
            .join(Event, Registration.event_id == Event.id)
            .filter(Event.organizer_id == current_user.id, Registration.status == "Confirmed")
            .scalar()
            or 0
        )
        total_vol_apps = (
            db.query(func.count(Volunteer.id))
            .join(Event, Volunteer.event_id == Event.id)
            .filter(Event.organizer_id == current_user.id)
            .scalar()
            or 0
        )
        organizer_stats = {
            "total_events_created": total_created,
            "upcoming_events": org_upcoming,
            "completed_events": org_completed,
            "total_participants": total_attendees,
            "volunteer_applications": total_vol_apps,
        }

    return {
        "total_registered_events": total_registered,
        "upcoming_events": upcoming_count,
        "completed_events": completed_count,
        "volunteer_applications": volunteer_count,
        "unread_notifications": unread_notifications,
        "organizer_stats": organizer_stats,
    }
