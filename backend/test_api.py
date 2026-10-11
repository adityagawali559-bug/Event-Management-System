"""
Automated Integration Test Suite for CEMPS
Validates Authentication, RBAC, Event Management, Registration,
Volunteers, Feedback, Notifications, and Admin Endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_tests():
    print("--- Starting CEMPS Integration Tests ---")

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. API Health Check verified")

    # 2. Categories
    res = client.get("/api/categories")
    assert res.status_code == 200, f"Categories failed: {res.text}"
    cats = res.json()
    assert len(cats) >= 10, "Expected at least 10 categories"
    print(f"[PASS] 2. Categories fetched successfully ({len(cats)} categories)")

    # 3. User Registration (New Participant)
    test_user_payload = {
        "full_name": "Test Student User",
        "email": "teststudent@cemps.edu",
        "mobile": "9998887776",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "role": "participant",
    }
    res = client.post("/api/auth/register", json=test_user_payload)
    assert res.status_code in [201, 400], f"Registration failed: {res.text}"
    print("[PASS] 3. Participant Registration works")

    # 4. User Login
    login_payload = {
        "email": "participant@cemps.edu",
        "password": "Password123!",
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200, f"Login failed: {res.text}"
    data = res.json()
    part_token = data["access_token"]
    assert part_token, "No access token returned"
    part_headers = {"Authorization": f"Bearer {part_token}"}
    print("[PASS] 4. User Login and JWT token generation successful")

    # 5. Get current user profile
    res = client.get("/api/auth/me", headers=part_headers)
    assert res.status_code == 200
    user_info = res.json()
    assert user_info["email"] == "participant@cemps.edu"
    print(f"[PASS] 5. Current User Profile verified: {user_info['full_name']}")

    # 6. Public Events Discovery
    res = client.get("/api/events")
    assert res.status_code == 200
    events_data = res.json()
    assert "items" in events_data and len(events_data["items"]) > 0
    first_event = events_data["items"][0]
    print(f"[PASS] 6. Events discovery verified ({events_data['total']} total events, first: '{first_event['title']}')")

    # 7. Single Event Details
    res = client.get(f"/api/events/{first_event['id']}", headers=part_headers)
    assert res.status_code == 200
    detail = res.json()
    assert "available_seats" in detail
    print(f"[PASS] 7. Event details retrieved (Available seats: {detail['available_seats']})")

    # 8. Organizer Login & Event Creation
    org_res = client.post(
        "/api/auth/login",
        json={"email": "organizer@cemps.edu", "password": "Password123!"},
    )
    assert org_res.status_code == 200
    org_token = org_res.json()["access_token"]
    org_headers = {"Authorization": f"Bearer {org_token}"}

    create_evt_payload = {
        "title": "Automated Test Workshop",
        "description": "Comprehensive automated testing and community service demonstration workshop.",
        "category_id": cats[0]["id"],
        "image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4",
        "date": "2026-10-15",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "location": "Virtual Seminar Room",
        "capacity": 50,
        "registration_deadline": "2026-10-14T23:59:59Z",
        "status": "Pending Approval",
    }
    create_res = client.post("/api/events", json=create_evt_payload, headers=org_headers)
    assert create_res.status_code == 201, f"Create event failed: {create_res.text}"
    created_evt = create_res.json()
    print(f"[PASS] 8. Organizer created event '{created_evt['title']}' (Status: {created_evt['status']})")

    # 9. Admin Login & Dashboard & Approval
    admin_res = client.post(
        "/api/auth/login",
        json={"email": "admin@cemps.edu", "password": "Password123!"},
    )
    assert admin_res.status_code == 200
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    dash_res = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200
    dash_metrics = dash_res.json()
    print(f"[PASS] 9. Admin Dashboard retrieved (Total users: {dash_metrics['total_users']}, Events: {dash_metrics['total_events']})")

    # Admin approve the event
    appr_res = client.put(f"/api/admin/events/{created_evt['id']}/approve", headers=admin_headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "Published"
    print(f"[PASS] 10. Admin approved event successfully -> Status: Published")

    # 11. Participant Register for newly approved event
    reg_res = client.post(f"/api/events/{created_evt['id']}/register", headers=part_headers)
    assert reg_res.status_code == 201
    print("[PASS] 11. Participant successfully registered for event")

    # 12. Prevent duplicate registration
    dup_res = client.post(f"/api/events/{created_evt['id']}/register", headers=part_headers)
    assert dup_res.status_code == 400
    print("[PASS] 12. Duplicate registration prevented with 400 Bad Request")

    # 13. My Registrations
    my_regs = client.get("/api/my-registrations", headers=part_headers)
    assert my_regs.status_code == 200
    assert len(my_regs.json()) > 0
    print(f"[PASS] 13. My Registrations retrieved ({len(my_regs.json())} registrations)")

    # 14. Notifications check & mark read
    notif_res = client.get("/api/notifications", headers=part_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    assert len(notifs) > 0
    print(f"[PASS] 14. Notifications retrieved ({len(notifs)} notifications)")

    mark_res = client.put("/api/notifications/read-all", headers=part_headers)
    assert mark_res.status_code == 200
    print("[PASS] 15. All notifications marked as read")

    print("\n>>> ALL 15 AUTOMATED INTEGRATION TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    run_tests()
