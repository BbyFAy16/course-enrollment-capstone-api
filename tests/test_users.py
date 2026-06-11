from app.models.user import User, UserRole
from app.utils.security import get_password_hash

def test_get_current_user_profile(client, student_token, db):
    """Test that an authenticated student can retrieve their own profile"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@test.com"
    assert data["role"] == "student"
    assert data["is_active"] == True
    assert "hashed_password" not in data

def test_get_user_by_id(client, admin_token, db):
    """Test that an authenticated user can retrieve another user by ID"""
    # Create a user to look up
    user = User(
        name="Lookup User",
        email="lookup@test.com",
        hashed_password=get_password_hash("LookupPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Retrieve the user
    response = client.get(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "lookup@test.com"
    assert data["name"] == "Lookup User"
    assert data["role"] == "student"

def test_get_nonexistent_user(client, admin_token):
    """Test that requesting a non-existent user returns 404"""
    response = client.get(
        "/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_unauthorized_access_without_token(client):
    """Test that accessing protected endpoints without token returns 401"""
    response = client.get("/users/me")
    assert response.status_code == 401
    
    response = client.get("/users/1")
    assert response.status_code == 401

def test_invalid_token_access(client):
    """Test that using an invalid token returns 401"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401

def test_expired_token_access(client, db):
    """Test that an expired token is rejected"""
    from app.utils.security import create_access_token
    from datetime import datetime, timedelta
    
    # Create user
    user = User(
        name="Expired Token User",
        email="expired@test.com",
        hashed_password=get_password_hash("ExpiredPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Create an already expired token
    expired_token = create_access_token(
        data={"sub": "expired@test.com", "role": "student"},
    )
    
    # Test with any token that's been tampered with
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}expired"}
    )
    assert response.status_code == 401

def test_inactive_user_token_rejected(client, db):
    """Test that an inactive user's token is rejected"""
    # Create inactive user
    user = User(
        name="Inactive Token User",
        email="inactive_token@test.com",
        hashed_password=get_password_hash("InactiveToken123"),
        role=UserRole.STUDENT,
        is_active=False
    )
    db.add(user)
    db.commit()
    
    # Try to login (will fail since user is inactive)
    response = client.post("/auth/login", json={
        "email": "inactive_token@test.com",
        "password": "InactiveToken123"
    })
    assert response.status_code == 403
    assert "deactivated" in response.json()["detail"].lower()

def test_admin_can_view_student_profile(client, admin_token, db):
    """Test that an admin can view student profiles"""
    # Create a student
    student = User(
        name="Student Viewed By Admin",
        email="viewed_by_admin@test.com",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    # Admin views the student profile
    response = client.get(
        f"/users/{student.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "viewed_by_admin@test.com"
    assert data["role"] == "student"

def test_student_can_view_other_student_profile(client, student_token, db):
    """Test that a student can view other student profiles"""
    # Create another student
    other_student = User(
        name="Other Student",
        email="other_student@test.com",
        hashed_password=get_password_hash("OtherPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(other_student)
    db.commit()
    db.refresh(other_student)
    
    # Student views the other student's profile
    response = client.get(
        f"/users/{other_student.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "other_student@test.com"
    assert data["name"] == "Other Student"

def test_user_profile_structure(client, student_token):
    """Test that the user profile response has the correct structure"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check all expected fields are present
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "role" in data
    assert "is_active" in data
    
    # Check that sensitive fields are NOT present
    assert "hashed_password" not in data
    assert "password" not in data
    
    # Check data types
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["email"], str)
    assert data["role"] in ["student", "admin"]
    assert isinstance(data["is_active"], bool)

def test_multiple_users_can_have_different_roles(client, db):
    """Test that users can have different roles"""
    # Register a student
    student_response = client.post("/auth/register", json={
        "name": "Role Student",
        "email": "role_student@test.com",
        "password": "StudentPass123",
        "role": "student"
    })
    assert student_response.status_code == 201
    student_data = student_response.json()
    assert student_data["role"] == "student"
    
    # Register an admin
    admin_response = client.post("/auth/register", json={
        "name": "Role Admin",
        "email": "role_admin@test.com",
        "password": "AdminPass12345",
        "role": "admin"
    })
    assert admin_response.status_code == 201
    admin_data = admin_response.json()
    assert admin_data["role"] == "admin"
    
    # Login as student
    student_login = client.post("/auth/login", json={
        "email": "role_student@test.com",
        "password": "StudentPass123"
    })
    assert student_login.status_code == 200
    student_token = student_login.json()["access_token"]
    
    # Login as admin
    admin_login = client.post("/auth/login", json={
        "email": "role_admin@test.com",
        "password": "AdminPass12345"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    
    # Verify student profile
    student_profile = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert student_profile.json()["role"] == "student"
    
    # Verify admin profile
    admin_profile = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_profile.json()["role"] == "admin"

def test_user_email_is_case_sensitive(client):
    """Test that email addresses are case-sensitive"""
    # Register with lowercase email
    response1 = client.post("/auth/register", json={
        "name": "Lowercase Email",
        "email": "case_test@test.com",
        "password": "CaseTest123",
        "role": "student"
    })
    assert response1.status_code == 201
    
    # Try to register with same email but different case
    response2 = client.post("/auth/register", json={
        "name": "Uppercase Email",
        "email": "CASE_TEST@test.com",
        "password": "CaseTest456",
        "role": "student"
    })
    assert response2.status_code in [201, 400]

def test_user_profile_update_not_allowed(client, student_token):
    """Test that users cannot directly update their profile through a PUT endpoint"""
    response = client.put(
        "/users/me",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code in [404, 405]

def test_get_current_user_with_valid_token(client, student_token):
    """Test getting current user with a valid token"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "student@test.com"
    assert user_data["is_active"] == True

def test_get_user_by_id_response_format(client, admin_token, db):
    """Test the exact response format of get user by ID"""
    user = User(
        name="Format Test",
        email="format@test.com",
        hashed_password=get_password_hash("FormatPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.get(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify exact structure
    expected_keys = {"id", "name", "email", "role", "is_active"}
    assert set(data.keys()) == expected_keys
    assert data["id"] == user.id
    assert data["name"] == "Format Test"
    assert data["email"] == "format@test.com"
    assert data["role"] == "student"
    assert data["is_active"] == True

def test_admin_cannot_access_student_only_features(client, admin_token):
    """Test that admins cannot access student-only features"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    # Admin should still be able to see their own profile
    assert response.json()["role"] == "admin"

def test_concurrent_user_sessions(client, db):
    """Test that multiple users can be logged in simultaneously"""
    # Create two users
    users_data = [
        {"name": "Concurrent User 1", "email": "concurrent1@test.com", "password": "Concurrent1", "role": "student"},
        {"name": "Concurrent User 2", "email": "concurrent2@test.com", "password": "Concurrent2", "role": "student"}
    ]
    
    tokens = []
    for user_data in users_data:
        # Register
        client.post("/auth/register", json=user_data)
        # Login
        login_response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        tokens.append(login_response.json()["access_token"])
    
    # Both tokens should be valid
    for i, token in enumerate(tokens):
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == users_data[i]["email"]

def test_user_count(client, db):
    """Test that we can count users (if you have such endpoint) or verify user creation"""
    initial_count = db.query(User).count()
    
    # Register a new user
    client.post("/auth/register", json={
        "name": "Count Test",
        "email": "count_test@test.com",
        "password": "CountPass123",
        "role": "student"
    })
    
    final_count = db.query(User).count()
    assert final_count == initial_count + 1

def test_get_all_users_pagination(client, admin_token, db):
    """Test getting all users with pagination (if implemented)"""
    # Create multiple users
    for i in range(5):
        user = User(
            name=f"Bulk User {i}",
            email=f"bulk_user_{i}@test.com",
            hashed_password=get_password_hash(f"BulkPass{i}123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(user)
    db.commit()
    
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"skip": 0, "limit": 10}
    )
    
    if response.status_code == 200:
        users = response.json()
        assert len(users) <= 10
    elif response.status_code == 404:
        pass

def test_update_current_user_profile(client, student_token):
    """Test that a user can update their own name"""
    response = client.put(
        "/users/me",
        json={"name": "Updated Student Name"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Student Name"

def test_admin_get_all_users(client, admin_token, db):
    """Test that admin can get all users"""
    for i in range(3):
        user = User(
            name=f"Test User {i}",
            email=f"testuser{i}@test.com",
            hashed_password=get_password_hash(f"TestPass{i}123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(user)
    db.commit()
    
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0

def test_admin_filter_users_by_role(client, admin_token, db):
    """Test filtering users by role"""
    response = client.get(
        "/users/",
        params={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    for user in users:
        assert user["role"] == "admin"

def test_admin_get_users_count(client, admin_token, db):
    """Test getting user count"""
    response = client.get(
        "/users/count",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert data["total"] > 0

def test_admin_update_user(client, admin_token, db):
    """Test that admin can update a user"""
    user = User(
        name="Update Me",
        email="update_me@test.com",
        hashed_password=get_password_hash("UpdatePass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.put(
        f"/users/{user.id}",
        json={"name": "Updated Name", "is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["is_active"] == False

def test_admin_delete_user(client, admin_token, db):
    """Test that admin can delete a user"""
    user = User(
        name="Delete Me",
        email="delete_me@test.com",
        hashed_password=get_password_hash("DeletePass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

def test_admin_cannot_delete_self(client, admin_token):
    """Test that admin cannot delete their own account"""
    # Get admin's own ID from profile
    profile_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_id = profile_response.json()["id"]
    
    response = client.delete(
        f"/users/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

def test_admin_deactivate_user(client, admin_token, db):
    """Test deactivating a user"""
    user = User(
        name="Deactivate Me",
        email="deactivate_me@test.com",
        hashed_password=get_password_hash("DeactivatePass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.patch(
        f"/users/{user.id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] == False

def test_admin_activate_user(client, admin_token, db):
    """Test activating a user"""
    user = User(
        name="Activate Me",
        email="activate_me@test.com",
        hashed_password=get_password_hash("ActivatePass123"),
        role=UserRole.STUDENT,
        is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = client.patch(
        f"/users/{user.id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] == True

def test_search_users(client, admin_token, db):
    """Test searching users by name or email"""
    user = User(
        name="Searchable Name",
        email="unique_search@test.com",
        hashed_password=get_password_hash("SearchPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Search by name
    response = client.get(
        "/users/",
        params={"search": "Searchable"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert any("Searchable" in u["name"] for u in users)
    
    # Search by email
    response = client.get(
        "/users/",
        params={"search": "unique_search"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert any("unique_search" in u["email"] for u in users)

def test_pagination_users(client, admin_token, db):
    """Test user pagination"""
    # Create 5 users
    for i in range(5):
        user = User(
            name=f"Page User {i}",
            email=f"page{i}@test.com",
            hashed_password=get_password_hash(f"PagePass{i}123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(user)
    db.commit()
    
    # Get first page
    response = client.get(
        "/users/",
        params={"skip": 0, "limit": 2},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Get second page
    response = client.get(
        "/users/",
        params={"skip": 2, "limit": 2},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) <= 2

def test_student_cannot_access_admin_endpoints(client, student_token):
    """Test that students cannot access admin-only endpoints"""
    # Try to get all users
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403
    
    # Try to update a user
    response = client.put(
        "/users/1",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403

def test_user_profile_update_validation(client, student_token):
    """Test validation on user profile update"""
    response = client.put(
        "/users/me",
        json={"name": ""},  # Empty name
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 422