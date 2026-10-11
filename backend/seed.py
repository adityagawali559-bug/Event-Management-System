"""
Seed script to populate initial sample data for CEMPS.
Creates categories, sample admin, organizers, participants, events,
registrations, volunteers, feedback, announcements, and notifications.
"""
from datetime import date, time, datetime, timedelta, timezone
from app.database.database import SessionLocal, init_db
from app.models.user import User
from app.models.category import Category
from app.models.event import Event
from app.models.registration import Registration
from app.models.volunteer import Volunteer
from app.models.feedback import Feedback
from app.models.announcement import Announcement
from app.models.notification import Notification
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
        # Default demo password for all sample accounts: "Password123!"
        hashed_pw = get_password_hash("Password123!")

        users_data = [
            # Admin
            {
                "email": "admin@cemps.edu",
                "full_name": "Prof. Rajesh Sharma (Dean CEP)",
                "mobile": "9876543210",
                "role": "admin",
            },
            # Organizers
            {
                "email": "organizer@cemps.edu",
                "full_name": "Dr. Ananya Roy (NSS Coordinator)",
                "mobile": "9876543211",
                "role": "organizer",
            },
            {
                "email": "rotaract@cemps.edu",
                "full_name": "Rohan Deshmukh (Rotaract President)",
                "mobile": "9876543212",
                "role": "organizer",
            },
            # Participants
            {
                "email": "participant@cemps.edu",
                "full_name": "Aarav Patel (Student)",
                "mobile": "9876543220",
                "role": "participant",
            },
            {
                "email": "priya.sharma@cemps.edu",
                "full_name": "Priya Sharma (Student)",
                "mobile": "9876543221",
                "role": "participant",
            },
            {
                "email": "neha.verma@cemps.edu",
                "full_name": "Neha Verma (Volunteer)",
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

        admin_user = user_map["admin@cemps.edu"]
        org_ananya = user_map["organizer@cemps.edu"]
        org_rohan = user_map["rotaract@cemps.edu"]
        part_aarav = user_map["participant@cemps.edu"]
        part_priya = user_map["priya.sharma@cemps.edu"]
        part_neha = user_map["neha.verma@cemps.edu"]

        # 3. Sample Events
        today = date.today()
        now_utc = datetime.now(timezone.utc)

        events_data = [
            {
                "title": "Green Campus Tree Plantation & Cleanliness Drive",
                "description": "Join hands with the NSS team and local civic body to plant 500 indigenous trees around the campus perimeter. Tools, saplings, gloves, and refreshments will be provided to all volunteers and participants.",
                "category": category_map["Environment"],
                "organizer": org_ananya,
                "image_url": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=7),
                "start_time": time(8, 30),
                "end_time": time(12, 0),
                "location": "Central Campus Quadrangle & Eco Park",
                "capacity": 100,
                "registration_deadline": now_utc + timedelta(days=5),
                "status": "Published",
            },
            {
                "title": "Youth Community Blood Donation & Health Checkup",
                "description": "Annual voluntary blood donation drive organized in association with the Red Cross Blood Bank. Free general health checkup including hemoglobin, BMI, and blood pressure screening.",
                "category": category_map["Health"],
                "organizer": org_ananya,
                "image_url": "https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=12),
                "start_time": time(9, 30),
                "end_time": time(16, 30),
                "location": "College Auditorium Hall B",
                "capacity": 150,
                "registration_deadline": now_utc + timedelta(days=10),
                "status": "Published",
            },
            {
                "title": "Digital Literacy Workshop for Community Elders",
                "description": "A student-led community outreach initiative teaching senior citizens how to use smartphones, access digital government services, use UPI securely, and navigate WhatsApp.",
                "category": category_map["Community"],
                "organizer": org_rohan,
                "image_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=15),
                "start_time": time(10, 0),
                "end_time": time(13, 0),
                "location": "IT Center Lab 301",
                "capacity": 40,
                "registration_deadline": now_utc + timedelta(days=13),
                "status": "Published",
            },
            {
                "title": "Inter-College Social Innovation Hackathon 2026",
                "description": "24-hour sprint to develop technology-driven solutions for local urban challenges, municipal waste management, and renewable energy monitoring. Prizes worth ₹50,000.",
                "category": category_map["Technology"],
                "organizer": org_rohan,
                "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=22),
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "location": "Innovation & Incubation Hub, 4th Floor",
                "capacity": 80,
                "registration_deadline": now_utc + timedelta(days=18),
                "status": "Published",
            },
            {
                "title": "Cultural Folk Music and Art Exhibition",
                "description": "Celebrating regional folk arts, indigenous crafts, and musical performances by rural artisan cooperatives. Open to public visitors and college families.",
                "category": category_map["Cultural"],
                "organizer": org_ananya,
                "image_url": "https://images.unsplash.com/photo-1460723237483-7a6dc9d0b212?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=28),
                "start_time": time(17, 0),
                "end_time": time(21, 0),
                "location": "Open Air Amphitheatre",
                "capacity": 250,
                "registration_deadline": now_utc + timedelta(days=25),
                "status": "Published",
            },
            {
                "title": "Community Sports Gala & Charity Marathon 5K",
                "description": "5-kilometer charity fun run to raise awareness for mental well-being and adolescent education. Finishers receive medals, certificates, and complimentary hydration packs.",
                "category": category_map["Sports"],
                "organizer": org_rohan,
                "image_url": "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=35),
                "start_time": time(6, 0),
                "end_time": time(10, 0),
                "location": "Main Sports Complex Ground",
                "capacity": 300,
                "registration_deadline": now_utc + timedelta(days=30),
                "status": "Published",
            },
            {
                "title": "Solar Energy & Sustainable Living Seminar",
                "description": "Technical seminar by climate engineers detailing rooftop solar installations, rainwater harvesting, and composting for residential societies.",
                "category": category_map["Seminar"],
                "organizer": org_ananya,
                "image_url": "https://images.unsplash.com/photo-1509391365360-2e959784a276?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=40),
                "start_time": time(14, 0),
                "end_time": time(17, 0),
                "location": "Seminar Hall C",
                "capacity": 60,
                "registration_deadline": now_utc + timedelta(days=36),
                "status": "Pending Approval",  # Demo of pending approval!
            },
            {
                "title": "Hands-On Robotics for High School Kids",
                "description": "Draft weekend session introducing Arduino microcontrollers and line-follower robots to visiting high school students.",
                "category": category_map["Workshop"],
                "organizer": org_rohan,
                "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop&q=80",
                "date": today + timedelta(days=45),
                "start_time": time(10, 0),
                "end_time": time(15, 0),
                "location": "Robotics Lab 102",
                "capacity": 30,
                "registration_deadline": now_utc + timedelta(days=41),
                "status": "Draft",  # Demo of draft!
            },
        ]

        created_events = []
        for ed in events_data:
            evt = db.query(Event).filter(Event.title == ed["title"]).first()
            if not evt:
                evt = Event(
                    title=ed["title"],
                    description=ed["description"],
                    category_id=ed["category"].id,
                    organizer_id=ed["organizer"].id,
                    image_url=ed["image_url"],
                    date=ed["date"],
                    start_time=ed["start_time"],
                    end_time=ed["end_time"],
                    location=ed["location"],
                    capacity=ed["capacity"],
                    registration_deadline=ed["registration_deadline"],
                    status=ed["status"],
                )
                db.add(evt)
                db.flush()
            created_events.append(evt)
        print(f"Events ready: {len(created_events)}")

        # 4. Registrations
        # Register Aarav for event 0 & 1
        ev0 = created_events[0]
        ev1 = created_events[1]
        ev2 = created_events[2]

        reg0 = db.query(Registration).filter(Registration.user_id == part_aarav.id, Registration.event_id == ev0.id).first()
        if not reg0:
            reg0 = Registration(user_id=part_aarav.id, event_id=ev0.id, status="Confirmed")
            db.add(reg0)

        reg1 = db.query(Registration).filter(Registration.user_id == part_aarav.id, Registration.event_id == ev1.id).first()
        if not reg1:
            reg1 = Registration(user_id=part_aarav.id, event_id=ev1.id, status="Confirmed")
            db.add(reg1)

        # Register Priya for event 0 & 2
        reg2 = db.query(Registration).filter(Registration.user_id == part_priya.id, Registration.event_id == ev0.id).first()
        if not reg2:
            reg2 = Registration(user_id=part_priya.id, event_id=ev0.id, status="Confirmed")
            db.add(reg2)

        reg3 = db.query(Registration).filter(Registration.user_id == part_priya.id, Registration.event_id == ev2.id).first()
        if not reg3:
            reg3 = Registration(user_id=part_priya.id, event_id=ev2.id, status="Confirmed")
            db.add(reg3)

        # 5. Volunteer Applications
        vol0 = db.query(Volunteer).filter(Volunteer.user_id == part_neha.id, Volunteer.event_id == ev0.id).first()
        if not vol0:
            vol0 = Volunteer(user_id=part_neha.id, event_id=ev0.id, status="Approved")
            db.add(vol0)

        vol1 = db.query(Volunteer).filter(Volunteer.user_id == part_aarav.id, Volunteer.event_id == ev2.id).first()
        if not vol1:
            vol1 = Volunteer(user_id=part_aarav.id, event_id=ev2.id, status="Pending")
            db.add(vol1)

        # 6. Sample Feedback
        fb0 = db.query(Feedback).filter(Feedback.user_id == part_priya.id, Feedback.event_id == ev0.id).first()
        if not fb0:
            fb0 = Feedback(
                user_id=part_priya.id,
                event_id=ev0.id,
                rating=5,
                comment="Wonderful community initiative! Very well coordinated by the NSS student coordinators.",
            )
            db.add(fb0)

        # 7. Sample Announcement
        ann0 = db.query(Announcement).filter(Announcement.event_id == ev0.id).first()
        if not ann0:
            ann0 = Announcement(
                event_id=ev0.id,
                organizer_id=org_ananya.id,
                message="Reminder: Please wear comfortable shoes and carry your reusable water bottle. Refreshments and planting tools will be provided at the entrance desk.",
            )
            db.add(ann0)

        # 8. Notifications
        notifs = [
            (
                part_aarav.id,
                f"Registration confirmed! You are registered for '{ev0.title}'.",
                "registration_confirmed",
            ),
            (
                part_aarav.id,
                f"New announcement for '{ev0.title}': Please wear comfortable shoes and carry your reusable water bottle.",
                "organizer_announcement",
            ),
            (
                part_neha.id,
                f"Your volunteer application for '{ev0.title}' was APPROVED!",
                "volunteer_status",
            ),
            (
                org_ananya.id,
                "New pending registration: Priya Sharma joined your Green Campus Drive.",
                "new_participant",
            ),
            (
                admin_user.id,
                "New event submitted for review: 'Solar Energy & Sustainable Living Seminar'.",
                "event_submission",
            ),
        ]

        for uid, msg, n_type in notifs:
            notif = Notification(user_id=uid, message=msg, notification_type=n_type, is_read=False)
            db.add(notif)

        db.commit()
        print("CEMPS database populated successfully with realistic sample data!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
