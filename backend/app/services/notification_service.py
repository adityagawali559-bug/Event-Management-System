from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    message: str,
    notification_type: str,
) -> Notification:
    """Create an in-app notification for a given user."""
    notif = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def notify_all_participants(
    db: Session,
    user_ids: list[int],
    message: str,
    notification_type: str,
):
    """Bulk create notifications for multiple users."""
    for uid in user_ids:
        notif = Notification(
            user_id=uid,
            message=message,
            notification_type=notification_type,
            is_read=False,
        )
        db.add(notif)
    db.commit()
