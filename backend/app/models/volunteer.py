from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="Pending", nullable=False)  # Pending, Approved, Rejected, Completed
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_volunteer"),
    )

    # Relationships
    user = relationship("User", back_populates="volunteer_applications")
    event = relationship("Event", back_populates="volunteers")

    def __repr__(self):
        return f"<Volunteer id={self.id} user_id={self.user_id} event_id={self.event_id} status='{self.status}'>"
