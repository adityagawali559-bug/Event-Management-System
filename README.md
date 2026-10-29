# Community Event Management and Participation System (CEMPS)
> **College Community Engagement Project (CEP)**  
> A complete, production-style, beginner-friendly full-stack web application connecting colleges, students, NGOs, and community organizers.

---

## 1. Project Overview

The **Community Event Management and Participation System (CEMPS)** is a modernized web application designed to replace fragmented, manual event coordination methods (paper registration sheets, spreadsheets, unstructured WhatsApp messages) with a unified, transparent digital portal.

Colleges, student clubs (NSS, Rotaract, IEEE, CSI), NGOs, and civic organizations can:
- Post, manage, and coordinate community drives (tree plantation, blood donation, coding bootcamps, elderly outreach).
- Streamline seat availability and enforce hard registration capacity limits.
- Manage student volunteers, assign duties, and track approvals.
- Broadcast instant announcements to attendees.
- Collect verified attendee ratings and reviews post-event for institutional CEP accreditation.

---

## 2. Core Features & Functional Modules

| Module | Features & Capabilities |
| :--- | :--- |
| **Authentication & RBAC** | Secure JWT Bearer authentication, bcrypt salted hashing, role-based access control (`Participant`, `Organizer`, `Admin`). |
| **Event Discovery** | Public event cards with real-time seat availability countdowns, full-text search, category filtering, and pagination. |
| **Event Registration** | 9-step registration verification: deadline checks, capacity enforcement, database-level unique constraint preventing duplicate signups. |
| **Volunteer System** | Attendees can apply to volunteer; organizers can review, approve, or reject applicants with instant notification alerts. |
| **Organizer Workspace** | Dedicated dashboard to draft, edit, submit events for review, broadcast announcements, view participants, and manage volunteers. |
| **Admin Governance** | High-level control panel to review and approve/reject pending events, manage system users, toggle accounts, and configure categories. |
| **Notification Engine** | In-app notification center for approvals, rejections, registration confirmations, cancellations, and broadcast updates. |
| **Feedback & Reviews** | Post-event 1–5 star rating and feedback system, computing live average ratings and preventing duplicate submissions. |

---

## 3. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Fetch API.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 ORM, Alembic, Uvicorn, PyJWT, bcrypt.
- **Database:** PostgreSQL (with automatic zero-config SQLite fallback for local developer machines).
- **Architecture:** Layered RESTful API (`models` -> `schemas` -> `routers` -> `services` -> `dependencies`).
- **Containerization:** Docker & Docker Compose (PostgreSQL 16 + FastAPI).

---

## 4. System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend (HTML5 / Bootstrap 5 / ES6 Fetch API)"]
        UI1["Landing Page (index.html)"]
        UI2["Events Catalog (events.html)"]
        UI3["Dashboards (Participant & Organizer)"]
        UI4["Admin Control Center (admin.html)"]
    end

    subgraph Security ["Security & Auth Layer"]
        JWT["JWT Bearer Authentication"]
        RBAC["Role-Based Access Control"]
        BCRYPT["Bcrypt Password Hashing"]
    end

    subgraph Backend ["FastAPI RESTful Backend"]
        R_AUTH["Auth Router (/api/auth)"]
        R_EVT["Events Router (/api/events)"]
        R_REG["Registrations (/api/events/{id}/register)"]
        R_VOL["Volunteers (/api/events/{id}/volunteer)"]
        R_ADM["Admin Router (/api/admin)"]
        R_NOT["Notifications (/api/notifications)"]
        R_FB["Feedback (/api/events/{id}/feedback)"]
    end

    subgraph Database ["Relational Database (PostgreSQL / SQLAlchemy ORM)"]
        DB_USERS[("Users Table")]
        DB_CATS[("Categories Table")]
        DB_EVENTS[("Events Table")]
        DB_REGS[("Registrations Table")]
        DB_VOLS[("Volunteers Table")]
        DB_NOTIFS[("Notifications Table")]
        DB_FEEDBACK[("Feedback Table")]
        DB_ANNOUNCEMENTS[("Announcements Table")]
    end

    Client --> Security
    Security --> Backend
    Backend --> Database
```

---

## 5. Directory Structure

```text
cemps/
├── docker-compose.yml          # Multi-container orchestration (PostgreSQL + API)
├── run_project.bat             # 1-Click Windows Batch startup script
├── run_project.ps1             # PowerShell startup script
├── README.md                   # Full documentation & setup guide
├── PROJECT_REPORT.md           # College CEP submission & viva reference report
├── .env.example                # Root environment template
├── .gitignore                  # Git ignore rules
│
├── backend/
│   ├── Dockerfile              # Backend container definition
│   ├── alembic.ini             # Alembic database migration config
│   ├── requirements.txt        # Python dependency manifest
│   ├── .env.example            # Backend environment template
│   ├── .env                    # Active local environment variables
│   ├── seed.py                 # Sample database seeder
│   ├── test_api.py             # 15-point automated integration test suite
│   ├── alembic/                # Alembic migration revisions
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   └── app/
│       ├── main.py             # FastAPI entrypoint, CORS, static mounting
│       ├── core/
│       │   ├── config.py       # Pydantic & environment settings
│       │   └── security.py     # Bcrypt & JWT encoding/decoding
│       ├── database/
│       │   └── database.py     # Engine, SessionLocal, Base, get_db
│       ├── models/             # SQLAlchemy ORM database models
│       │   ├── user.py
│       │   ├── category.py
│       │   ├── event.py
│       │   ├── registration.py
│       │   ├── volunteer.py
│       │   ├── notification.py
│       │   ├── feedback.py
│       │   └── announcement.py
│       ├── schemas/            # Pydantic validation schemas
│       │   ├── user.py
│       │   ├── category.py
│       │   ├── event.py
│       │   ├── registration.py
│       │   ├── volunteer.py
│       │   ├── notification.py
│       │   ├── feedback.py
│       │   └── announcement.py
│       ├── routers/            # FastAPI API endpoints
│       │   ├── auth.py
│       │   ├── users.py
│       │   ├── categories.py
│       │   ├── events.py
│       │   ├── registrations.py
│       │   ├── volunteers.py
│       │   ├── notifications.py
│       │   ├── feedback.py
│       │   ├── announcements.py
│       │   └── admin.py
│       ├── services/           # Business logic layer
│       │   ├── event_service.py
│       │   └── notification_service.py
│       └── dependencies/       # Security & RBAC dependencies
│           └── auth.py
│
└── frontend/
    ├── index.html              # Home landing page with hero, stats, featured events
    ├── css/
    │   ├── style.css           # Modern custom CSS styling
    │   └── responsive.css      # Tablet and mobile viewport breakpoints
    ├── js/
    │   ├── api.js              # Central Fetch API wrapper
    │   ├── auth.js             # Session, login, registration, logout handler
    │   ├── common.js           # Toast alerts, navbar & footer renderers
    │   ├── events.js           # Event catalog, filters, details, registration
    │   ├── dashboard.js        # Participant and organizer metrics
    │   ├── registrations.js    # My Registrations and volunteer application tables
    │   ├── notifications.js    # In-app notification list and mark-as-read
    │   └── admin.js            # Admin panel, event approvals, user role management
    └── pages/
        ├── login.html          # Login page with demo quick-fill buttons
        ├── register.html       # Signup page with participant/organizer roles
        ├── events.html         # Event search, category filter, cards, pagination
        ├── event-details.html  # Full event banner, seats counter, register button
        ├── dashboard.html      # Participant & organizer dual dashboard
        ├── my-registrations.html # User ticket & volunteer management
        ├── create-event.html   # Organizer event submission form
        ├── manage-events.html  # Organizer event lifecycle & coordination tools
        ├── notifications.html  # Alerts and notification history
        ├── profile.html        # Account details and password updates
        ├── feedback.html       # Attendee star rating and comments form
        └── admin.html          # Dean / Admin governance control panel
```

---

## 6. Demo Credentials (For Evaluation & Viva)

All pre-seeded demo accounts share the password: **`Password123!`**

| Role | Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@cemps.edu` | `Password123!` | System statistics, approve/reject pending events, user role management, category CRUD |
| **Organizer** | `organizer@cemps.edu` | `Password123!` | Create events, submit drafts, broadcast participant announcements, approve volunteers |
| **Participant** | `participant@cemps.edu` | `Password123!` | Discover events, register, cancel tickets, apply as volunteer, submit feedback |
| **Student 2** | `priya.sharma@cemps.edu` | `Password123!` | Additional sample participant with active registrations |

*(Tip: On the login page, you can click the quick-fill buttons to automatically insert any of these credentials!)*

---

## 7. Step-by-Step Setup Guide

### Method A: Quick 1-Click Launch (Windows)
Double-click `run_project.bat` or run:
```powershell
.\run_project.ps1
```
This script will automatically create the virtual environment, install requirements, seed sample data, start the FastAPI server on port 8000, and open the web browser.

---

### Method B: Manual Local Setup (Python + SQLite/PostgreSQL)

#### 1. Navigate to the backend directory:
```bash
cd backend
```

#### 2. Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment (`.env`):
A default `.env` is pre-created in `backend/.env`. If you have PostgreSQL running, configure your connection string:
```ini
DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5432/cemps_db
SECRET_KEY=cemps_super_secret_jwt_key_college_project_2026_engagement_platform
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500
```
*(If PostgreSQL is not running locally, the project defaults gracefully to `sqlite:///./cemps.db` so you can test immediately with zero friction!)*

#### 5. Run Database Migrations & Seed Sample Data:
```bash
alembic upgrade head
python seed.py
```

#### 6. Run Automated Test Suite:
```bash
python test_api.py
```
*(All 15 automated integration tests will verify authentication, events, registrations, volunteers, and admin endpoints).*

#### 7. Start the Application:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

### Method C: Docker & Docker Compose (Full PostgreSQL + FastAPI)

If you have Docker installed:
```bash
docker compose up -d --build
```
This starts:
- A PostgreSQL 16 container with persistent volumes
- A FastAPI backend container connected to PostgreSQL on port 8000

---

## 8. Interactive API Documentation

Once the server is running, navigate to:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 9. Key Database Constraints & Integrity Rules

- **Duplicate Registrations:** Guarded at the database level using `UniqueConstraint("user_id", "event_id", name="uq_user_event_registration")`.
- **Duplicate Volunteers:** Prevented via `UniqueConstraint("user_id", "event_id", name="uq_user_event_volunteer")`.
- **Duplicate Feedback:** Prevented via `UniqueConstraint("user_id", "event_id", name="uq_user_event_feedback")`.
- **Cascade Deletion:** Foreign keys enforce `ondelete="CASCADE"` to ensure relational referential integrity.

---

## 10. Future Scope & Enhancements

1. **QR Code Attendance Verification:** Digital check-in scans at the event venue.
2. **Automated CEP Certificate Generation:** PDF participation certificate generation upon event completion.
3. **SMS / Email Alerts:** Integration with Twilio or SendGrid for external alerts.
4. **Geolocation Mapping:** Interactive Leaflet / Google Maps integration for venue routing.
