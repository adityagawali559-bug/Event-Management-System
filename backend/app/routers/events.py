from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, List
from datetime import date, datetime, timezone
import math

from app.database.database import get_db
from app.models.event import Event
from app.models.category import Category
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
)
from app.dependencies.auth import (
    get_current_user,
    get_optional_current_user,
    require_organizer,
)
from app.services.event_service import enrich_event_response
from app.services.notification_service import create_notification

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=EventListResponse)
def get_events(
    search: Optional[str] = Query(None, description="Search by title, location, or description"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    date_from: Optional[date] = Query(None, description="Filter events from date"),
    date_to: Optional[date] = Query(None, description="Filter events up to date"),
    location: Optional[str] = Query(None, description="Filter by location keyword"),
    status: Optional[str] = Query(None, description="Filter by status (Draft, Pending Approval, Published, etc.)"),
    organizer_id: Optional[int] = Query(None, description="Filter events by organizer"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    List events with filtering, search, and pagination.
    Public users only see 'Published' or 'Approved' events.
    Organizers and Admins can see draft/pending events according to their permissions.
    """
    query = db.query(Event)

    # Status visibility logic
    if current_user and current_user.role == "admin":
        if status:
            query = query.filter(Event.status == status)
    elif current_user and current_user.role == "organizer":
        if organizer_id == current_user.id or (status and status in ["Draft", "Pending Approval"]):
            # Organizer viewing their own events
            query = query.filter(
                or_(
                    Event.status.in_(["Published", "Approved", "Completed"]),
                    and_(Event.organizer_id == current_user.id, Event.status == status) if status else Event.organizer_id == current_user.id
                )
            )
        else:
            query = query.filter(Event.status.in_(["Published", "Approved", "Completed"]))
    else:
        # Public / Participant
        query = query.filter(Event.status.in_(["Published", "Approved", "Completed"]))

    # Specific filters
    if organizer_id:
        query = query.filter(Event.organizer_id == organizer_id)

    if category_id:
        query = query.filter(Event.category_id == category_id)

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    if date_from:
        query = query.filter(Event.date >= date_from)

    if date_to:
        query = query.filter(Event.date <= date_to)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Event.title.ilike(search_pattern),
                Event.description.ilike(search_pattern),
                Event.location.ilike(search_pattern),
            )
        )

    # Sort upcoming first
    total = query.count()
    query = query.order_by(Event.date.asc(), Event.start_time.asc())

    offset = (page - 1) * size
    events = query.offset(offset).limit(size).all()

    user_id = current_user.id if current_user else None
    items = [enrich_event_response(db, ev, current_user_id=user_id) for ev in events]
    pages = math.ceil(total / size) if total > 0 else 1

    return EventListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/featured/highlights", response_model=List[EventResponse])
def get_featured_events(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve up to 4 top upcoming published/approved events for the hero & featured sections."""
    today = date.today()
    events = (
        db.query(Event)
        .filter(Event.status.in_(["Published", "Approved"]), Event.date >= today)
        .order_by(Event.date.asc(), Event.capacity.desc())
        .limit(4)
        .all()
    )
    user_id = current_user.id if current_user else None
    return [enrich_event_response(db, ev, current_user_id=user_id) for ev in events]


@router.get("/{event_id}", response_model=EventResponse)
def get_event_details(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve comprehensive details of a single event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    # Access control for unpublished events
    if event.status not in ["Published", "Approved", "Completed"]:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event is not yet publicly visible.")
        if current_user.role != "admin" and event.organizer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event is not yet published.")

    user_id = current_user.id if current_user else None
    return enrich_event_response(db, event, current_user_id=user_id)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """
    Create a new event.
    Organizers submit events which start in 'Pending Approval' or 'Draft'.
    Admins can directly publish or approve events.
    """
    category = db.query(Category).filter(Category.id == event_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified category does not exist.",
        )

    # Initial status rule
    status_to_set = "Pending Approval"
    if current_user.role == "admin":
        status_to_set = event_in.status if event_in.status else "Published"
    else:
        if event_in.status == "Draft":
            status_to_set = "Draft"
        else:
            status_to_set = "Pending Approval"

    new_event = Event(
        title=event_in.title.strip(),
        description=event_in.description.strip(),
        category_id=event_in.category_id,
        image_url=event_in.image_url,
        date=event_in.date,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        location=event_in.location.strip(),
        capacity=event_in.capacity,
        registration_deadline=event_in.registration_deadline,
        organizer_id=current_user.id,
        status=status_to_set,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Notify organizer
    msg = f"Your event '{new_event.title}' was created with status: {new_event.status}."
    create_notification(db, current_user.id, msg, "event_status")

    return enrich_event_response(db, new_event, current_user_id=current_user.id)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """Update event information (Organizer owner or Admin)."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this event.")

    update_dict = event_in.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        if field == "status" and current_user.role != "admin" and val in ["Approved", "Published"]:
            # Normal organizer cannot self-approve
            continue
        setattr(event, field, val)

    db.commit()
    db.refresh(event)
    return enrich_event_response(db, event, current_user_id=current_user.id)


@router.post("/{event_id}/submit-approval", response_model=EventResponse)
def submit_for_approval(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """Submit a draft event for administrator review and approval."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    event.status = "Pending Approval"
    db.commit()
    db.refresh(event)

    create_notification(
        db,
        current_user.id,
        f"Event '{event.title}' was submitted for Admin approval.",
        "event_status",
    )
    return enrich_event_response(db, event, current_user_id=current_user.id)


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    """Delete an event (Organizer owner or Admin)."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if current_user.role != "admin" and event.organizer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully."}
