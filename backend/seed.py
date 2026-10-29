"""
Seed script to populate initial data for CEMPS.
Creates categories and default admin, organizer, and participant accounts.
No sample events are seeded — organizers can create events through the UI.
"""
from app.database.database import SessionLocal, init_db
from app.models.user import User
from app.models.category import Category
from app.core.security import get_password_hash


def seed_data():
    print("Initializing database tables...")
    init_db()
    db = SessionLocal()

    try:
        # 1. Categories
        categories_data = [
            ("Education", "Academic workshops, tutoring sessions, and study circles."),
            ("Technology", "Coding hackathons, AI seminars, and open source projects."),
            ("Sports", "Community tournaments, marathons, yoga, and fitness meets."),
            ("Cultural", "Music fests, arts, theater, and heritage celebrations."),
            ("Environment", "Tree plantation drives, beach cleanups, and recycling summits."),
            ("Health", "Blood donation camps, mental health webinars, and checkups."),
            ("Social Service", "Food distribution, elderly care visits, and NGO outreach."),
            ("Community", "Neighborhood townhalls, youth clubs, and networking circles."),
            ("Workshop", "Hands-on skill building, robotics, craft, and leadership."),
            ("Seminar", "Guest expert lectures, career guidance, and research talks."),
        ]

        category_map = {}
        for name, desc in categories_data:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(name=name, description=desc)
                db.add(cat)
                db.flush()
            category_map[name] = cat
        print(f"Categories ready: {len(category_map)}")

        # 2. Users (Admin, Organizers, Participants)
        # Default password for all accounts: "Password123!"
        hashed_pw = get_password_hash("Password123!")

        users_data = [
            # Admin
            {
                "email": "admin@cemps.edu",
                "full_name": "Admin",
                "mobile": "9876543210",
                "role": "admin",
            },
            # Organizers
            {
                "email": "organizer@cemps.edu",
                "full_name": "Aditya Nikam",
                "mobile": "9876543211",
                "role": "organizer",
            },
            {
                "email": "rotaract@cemps.edu",
                "full_name": "Aditya Nikam",
                "mobile": "9876543212",
                "role": "organizer",
            },
            # Participants
            {
                "email": "participant@cemps.edu",
                "full_name": "Aditya Gawali",
                "mobile": "9876543220",
                "role": "participant",
            },
            {
                "email": "priya.sharma@cemps.edu",
                "full_name": "Aditya Gawali",
                "mobile": "9876543221",
                "role": "participant",
            },
            {
                "email": "neha.verma@cemps.edu",
                "full_name": "Aditya Gawali",
                "mobile": "9876543222",
                "role": "participant",
            },
        ]

        user_map = {}
        for u in users_data:
            user = db.query(User).filter(User.email == u["email"]).first()
            if not user:
                user = User(
                    full_name=u["full_name"],
                    email=u["email"],
                    mobile=u["mobile"],
                    password_hash=hashed_pw,
                    role=u["role"],
                    is_active=True,
                )
                db.add(user)
                db.flush()
            user_map[u["email"]] = user
        print(f"Users ready: {len(user_map)}")

        db.commit()
        print("CEMPS database seeded successfully with categories and default accounts!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
