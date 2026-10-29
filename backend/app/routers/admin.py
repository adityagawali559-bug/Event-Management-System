from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_
from typing import List, Optional
from datetime import date

from app.database.database import get_db
from app.models.user import User
from app.models.event import Event
from app.models.category import Category
from app.models.registration import Registration
from app.models.volunteer import Volunteer
from app.schemas.user import UserResponse
from app.schemas.event import EventResponse
from app.dependencies.auth import require_admin
from app.services.event_service import enrich_event_response
from app.services.notification_service import create_notification

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def get_admin_dashboard_metrics(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Provide comprehensive aggregated metrics for the administrator dashboard."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_organizers = (
        db.query(func.count(User.id)).filter(User.role == "organizer").scalar() or 0
    )
    total_participants = (
        db.query(func.count(User.id)).filter(User.role == "participant").scalar() or 0
    )
    total_events = db.query(func.count(Event.id)).scalar() or 0
    pending_approvals = (
        db.query(func.count(Event.id)).filter(Event.status == "Pending Approval").scalar() or 0
    )
    total_registrations = (
        db.query(func.count(Registration.id)).filter(Registration.status == "Confirmed").scalar() or 0
    )
    active_events = (
        db.query(func.count(Event.id))
        .filter(Event.status.in_(["Published", "Approved"]), Event.date >= date.today())
        .scalar()
        or 0
    )
    completed_events = (
        db.query(func.count(Event.id))
        .filter(
            or_(
                Event.status == "Completed",
                and_(Event.status.in_(["Published", "Approved"]), Event.date < date.today()),
            )
        )
        .scalar()
        or 0
    )

    # Popular categories breakdown
    categories_stats = []
    cats = db.query(Category).all()
    for cat in cats:
        evt_count = db.query(func.count(Event.id)).filter(Event.category_id == cat.id).scalar() or 0
        categories_stats.append({
            "category_id": cat.id,
            "category_name": cat.name,
            "event_count": evt_count,
        })

    categories_stats.sort(key=lambda x: x["event_count"], reverse=True)

    # Recent registrations
    recent_regs_raw = (
        db.query(Registration)
        .order_by(Registration.registration_date.desc())
        .limit(5)
        .all()
    )
    recent_registrations = [
        {
            "id": r.id,
            "user_name": r.user.full_name if r.user else "N/A",
            "user_email": r.user.email if r.user else "N/A",
            "event_title": r.event.title if r.event else "N/A",
            "status": r.status,
            "registration_date": r.registration_date.isoformat(),
        }
        for r in recent_regs_raw
    ]

    return {
        "total_users": total_users,
        "total_organizers": total_organizers,
        "total_participants": total_participants,
        "total_events": total_events,
        "pending_approvals": pending_approvals,
        "total_registrations": total_registrations,
        "active_events": active_events,
        "completed_events": completed_events,
        "popular_categories": categories_stats,
        "recent_registrations": recent_registrations,
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """List all registered users with optional role and search filtering."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        s = f"%{search}%"
        query = query.filter(or_(User.full_name.ilike(s), User.email.ilike(s)))
    return query.order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Enable or disable user account access."""
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_active = is_active
    db.commit()
    return {"message": f"User status updated to {'Active' if is_active else 'Deactivated'}."}


@router.put("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Change role of a user (participant, organizer, admin)."""
    if new_role not in ["participant", "organizer", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role specified.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.role = new_role
    db.commit()
    return {"message": f"User role updated to '{new_role}'."}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete a user account (Admin only)."""
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own admin account.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully."}


@router.get("/events/pending", response_model=List[EventResponse])
def get_pending_events(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all events waiting for administrator approval."""
    events = (
        db.query(Event)
        .filter(Event.status == "Pending Approval")
        .order_by(Event.created_at.desc())
        .all()
    )
    return [enrich_event_response(db, ev, current_user_id=admin.id) for ev in events]


@router.put("/events/{event_id}/approve", response_model=EventResponse)
def approve_event(
    event_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Approve and publish an event, notifying the organizer."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    event.status = "Published"
    db.commit()
    db.refresh(event)

    create_notification(
        db,
        event.organizer_id,
        f"Congratulations! Your event '{event.title}' has been APPROVED and is now Published.",
        "event_approved",
    )

    return enrich_event_response(db, event, current_user_id=admin.id)


@router.put("/events/{event_id}/reject", response_model=EventResponse)
def reject_event(
    event_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Reject an event, notifying the organizer with reason if provided."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    event.status = "Rejected"
    db.commit()
    db.refresh(event)

    reason_text = f" Reason: {reason}" if reason else ""
    create_notification(
        db,
        event.organizer_id,
        f"Your event '{event.title}' was reviewed and REJECTED.{reason_text}",
        "event_rejected",
    )

    return enrich_event_response(db, event, current_user_id=admin.id)
