from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.announcement import Announcement
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse
from app.dependencies.auth import require_organizer
from app.services.notification_service import notify_all_participants

router = APIRouter(tags=["Announcements"])


@router.post("/events/{event_id}/announcements", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_event_announcement(
    event_id: int,
    ann_in: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """
    Post an announcement for an event.
    Automatically generates in-app notifications for all registered participants.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    ann = Announcement(
        event_id=event.id,
        organizer_id=current_user.id,
        message=ann_in.message.strip(),
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)

    # Fetch all confirmed participants and notify them
    regs = (
        db.query(Registration.user_id)
        .filter(Registration.event_id == event.id, Registration.status == "Confirmed")
        .all()
    )
    participant_ids = [r[0] for r in regs]
    if participant_ids:
        msg = f"Announcement for '{event.title}': {ann.message}"
        notify_all_participants(db, participant_ids, msg, "organizer_announcement")

    return AnnouncementResponse(
        id=ann.id,
        event_id=ann.event_id,
        organizer_id=ann.organizer_id,
        message=ann.message,
        created_at=ann.created_at,
        organizer_name=current_user.full_name,
        event_title=event.title,
    )


@router.get("/events/{event_id}/announcements", response_model=List[AnnouncementResponse])
def get_event_announcements(
    event_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all announcements published for an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    anns = (
        db.query(Announcement)
        .filter(Announcement.event_id == event_id)
        .order_by(Announcement.created_at.desc())
        .all()
    )
    return [
        AnnouncementResponse(
            id=a.id,
            event_id=a.event_id,
            organizer_id=a.organizer_id,
            message=a.message,
            created_at=a.created_at,
            organizer_name=a.organizer.full_name if a.organizer else "Organizer",
            event_title=event.title,
        )
        for a in anns
    ]
