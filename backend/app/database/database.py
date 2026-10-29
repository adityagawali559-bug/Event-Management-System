import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine connection arguments based on database dialect
db_url = settings.DATABASE_URL
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)
else:
    # PostgreSQL configuration with connection pooling
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides an independent database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database and seed default categories if missing."""
    # Import all models to ensure they are registered with Base.metadata
    from app.models import (
        user,
        category,
        event,
        registration,
        volunteer,
        notification,
        feedback,
        announcement,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")

    # Auto-seed standard categories if missing
    try:
        db = SessionLocal()
        default_categories = [
            ("Cultural", "Music fests, arts, theater, and heritage celebrations."),
            ("Education", "Academic workshops, tutoring sessions, and study circles."),
            ("Technology", "Coding hackathons, AI seminars, and open source projects."),
            ("Sports", "Community tournaments, marathons, yoga, and fitness meets."),
            ("Environment", "Tree plantation drives, beach cleanups, and recycling summits."),
            ("Health", "Blood donation camps, mental health webinars, and checkups."),
            ("Social Service", "Food distribution, elderly care visits, and NGO outreach."),
            ("Community", "Neighborhood townhalls, youth clubs, and networking circles."),
            ("Workshop", "Hands-on skill building, robotics, craft, and leadership."),
            ("Seminar", "Guest expert lectures, career guidance, and research talks."),
        ]
        for name, desc in default_categories:
            exists = db.query(category.Category).filter(category.Category.name == name).first()
            if not exists:
                db.add(category.Category(name=name, description=desc))
        db.commit()
        db.close()
        logger.info("Standard event categories verified/seeded.")
    except Exception as e:
        logger.warning(f"Could not auto-seed standard categories: {e}")

