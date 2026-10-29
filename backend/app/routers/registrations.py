from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import List

from app.database.database import get_db
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User
from app.schemas.registration import RegistrationResponse
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user, require_organizer
from app.services.event_service import get_registered_count
from app.services.notification_service import create_notification

router = APIRouter(tags=["Registrations"])


@router.post("/events/{event_id}/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register the logged-in user for an event:
    1. Verify user is authenticated (handled by get_current_user).
    2. Verify event exists and is Approved or Published.
    3. Verify registration deadline has not elapsed.
    4. Verify event capacity is not full.
    5. Verify user has not already registered.
    6. Insert registration and send notification.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if event.status not in ["Published", "Approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot register for an event with status '{event.status}'.",
        )

    # Check registration deadline
    now = datetime.now(timezone.utc)
    deadline = event.registration_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if now > deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline for this event has passed.",
        )

    # Check capacity
    confirmed_count = get_registered_count(db, event.id)
    if confirmed_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This event has reached its maximum capacity.",
        )

    # Check existing registration
    existing = (
        db.query(Registration)
        .filter(Registration.event_id == event_id, Registration.user_id == current_user.id)
        .first()
    )
    if existing:
        if existing.status == "Confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already registered for this event.",
            )
        elif existing.status == "Cancelled":
            # Re-activate registration
            existing.status = "Confirmed"
            existing.registration_date = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)

            # Notification
            create_notification(
                db,
                current_user.id,
                f"You have re-registered for '{event.title}'.",
                "registration_confirmed",
            )
            return build_reg_response(existing, event, current_user)

    # Create new registration
    new_reg = Registration(
        user_id=current_user.id,
        event_id=event.id,
        status="Confirmed",
    )
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)

    # In-app notification to participant
    create_notification(
        db,
        current_user.id,
        f"Registration confirmed! You are registered for '{event.title}' on {event.date}.",
        "registration_confirmed",
    )

    # Notify organizer of new participant
    create_notification(
        db,
        event.organizer_id,
        f"New registration: {current_user.full_name} registered for '{event.title}'.",
        "new_participant",
    )

    return build_reg_response(new_reg, event, current_user)


@router.get("/my-registrations", response_model=List[RegistrationResponse])
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all registrations for the currently authenticated user."""
    regs = (
        db.query(Registration)
        .join(Event, Registration.event_id == Event.id)
        .filter(Registration.user_id == current_user.id)
        .order_by(Event.date.desc())
        .all()
    )
    return [build_reg_response(r, r.event, current_user) for r in regs]


@router.delete("/registrations/{registration_id}")
def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an event registration and notify the participant."""
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found.")

    if reg.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    if reg.status == "Cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration is already cancelled.")

    reg.status = "Cancelled"
    db.commit()

    event = db.query(Event).filter(Event.id == reg.event_id).first()
    title = event.title if event else "the event"

    create_notification(
        db,
        reg.user_id,
        f"Your registration for '{title}' has been cancelled.",
        "registration_cancelled",
    )

    return {"message": "Registration successfully cancelled."}


@router.get("/events/{event_id}/participants", response_model=List[RegistrationResponse])
def get_event_participants(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """Organizer / Admin view of registered participants for an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    regs = (
        db.query(Registration)
        .filter(Registration.event_id == event_id)
        .order_by(Registration.registration_date.desc())
        .all()
    )
    return [build_reg_response(r, event, r.user) for r in regs]


def build_reg_response(reg: Registration, event: Event, user: User) -> RegistrationResponse:
    user_resp = UserResponse.model_validate(user) if user else None
    return RegistrationResponse(
        id=reg.id,
        user_id=reg.user_id,
        event_id=reg.event_id,
        registration_date=reg.registration_date,
        status=reg.status,
        user=user_resp,
        event_title=event.title if event else "Unknown",
        event_date=str(event.date) if event else "N/A",
        event_location=event.location if event else "N/A",
        event_status=event.status if event else "N/A",
        event_image_url=event.image_url if event else None,
    )
