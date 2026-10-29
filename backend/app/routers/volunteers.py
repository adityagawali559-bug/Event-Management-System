from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.volunteer import Volunteer
from app.models.event import Event
from app.models.user import User
from app.schemas.volunteer import VolunteerCreate, VolunteerUpdate, VolunteerResponse
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user, require_organizer
from app.services.notification_service import create_notification

router = APIRouter(tags=["Volunteers"])


@router.post("/events/{event_id}/volunteer", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
def apply_as_volunteer(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit volunteer application for an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if event.status not in ["Published", "Approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to volunteer for an unapproved event.",
        )

    existing = (
        db.query(Volunteer)
        .filter(Volunteer.event_id == event_id, Volunteer.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You have already applied as a volunteer (Status: {existing.status}).",
        )

    vol = Volunteer(
        user_id=current_user.id,
        event_id=event.id,
        status="Pending",
    )
    db.add(vol)
    db.commit()
    db.refresh(vol)

    create_notification(
        db,
        current_user.id,
        f"Your volunteer application for '{event.title}' has been submitted.",
        "volunteer_applied",
    )

    create_notification(
        db,
        event.organizer_id,
        f"{current_user.full_name} applied to volunteer for '{event.title}'.",
        "volunteer_applied",
    )

    return build_vol_response(vol, event, current_user)


@router.get("/my-volunteer-applications", response_model=List[VolunteerResponse])
def get_my_volunteer_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all volunteer applications submitted by the current user."""
    apps = (
        db.query(Volunteer)
        .join(Event, Volunteer.event_id == Event.id)
        .filter(Volunteer.user_id == current_user.id)
        .order_by(Volunteer.applied_at.desc())
        .all()
    )
    return [build_vol_response(v, v.event, current_user) for v in apps]


@router.get("/events/{event_id}/volunteers", response_model=List[VolunteerResponse])
def get_event_volunteers(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """Organizer/Admin view of volunteer applications for a specific event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    vols = (
        db.query(Volunteer)
        .filter(Volunteer.event_id == event_id)
        .order_by(Volunteer.applied_at.desc())
        .all()
    )
    return [build_vol_response(v, event, v.user) for v in vols]


@router.put("/volunteers/{volunteer_id}", response_model=VolunteerResponse)
def update_volunteer_status(
    volunteer_id: int,
    vol_in: VolunteerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """Approve or reject a volunteer application (Organizer or Admin)."""
    vol = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
    if not vol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer record not found.")

    event = db.query(Event).filter(Event.id == vol.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    vol.status = vol_in.status
    db.commit()
    db.refresh(vol)

    # In-app notification to volunteer
    create_notification(
        db,
        vol.user_id,
        f"Your volunteer application for '{event.title}' was updated to '{vol.status}'.",
        "volunteer_status",
    )

    return build_vol_response(vol, event, vol.user)


def build_vol_response(vol: Volunteer, event: Event, user: User) -> VolunteerResponse:
    user_resp = UserResponse.model_validate(user) if user else None
    return VolunteerResponse(
        id=vol.id,
        user_id=vol.user_id,
        event_id=vol.event_id,
        status=vol.status,
        applied_at=vol.applied_at,
        updated_at=vol.updated_at,
        user=user_resp,
        event_title=event.title if event else "Unknown",
        event_date=str(event.date) if event else "N/A",
        event_location=event.location if event else "N/A",
    )
