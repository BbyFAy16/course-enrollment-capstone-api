def test_register_student(client):
    response = client.post("/auth/register", json={
        "name": "New Student",
        "email": "newstudent@test.com",
        "password": "NewPass123",
        "role": "student"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newstudent@test.com"
    assert data["role"] == "student"

def test_register_admin(client):
    response = client.post("/auth/register", json={
        "name": "New Admin",
        "email": "newadmin@test.com",
        "password": "AdminPass123",
        "role": "admin"
    })
    assert response.status_code == 201
    assert response.json()["role"] == "admin"

def test_register_duplicate_email(client):
    # Register first user
    client.post("/auth/register", json={
        "name": "User One",
        "email": "duplicate@test.com",
        "password": "Pass123456",
        "role": "student"
    })
    
    # Try to register with same email
    response = client.post("/auth/register", json={
        "name": "User Two",
        "email": "duplicate@test.com",
        "password": "Pass123456",
        "role": "student"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, db):
    # Create user first
    client.post("/auth/register", json={
        "name": "Login Test",
        "email": "logintest@test.com",
        "password": "LoginPass123",
        "role": "student"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "logintest@test.com",
        "password": "LoginPass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_inactive_user(client, db):
    from app.models.user import User, UserRole
    from app.utils.security import get_password_hash
    
    # Create inactive user directly
    user = User(
        name="Inactive User",
        email="inactive@test.com",
        hashed_password=get_password_hash("InactivePass123"),
        role=UserRole.STUDENT,
        is_active=False
    )
    db.add(user)
    db.commit()
    
    response = client.post("/auth/login", json={
        "email": "inactive@test.com",
        "password": "InactivePass123"
    })
    assert response.status_code == 403

def test_login_wrong_password(client, db):
    # Create user first
    client.post("/auth/register", json={
        "name": "Wrong Pass",
        "email": "wrongpass@test.com",
        "password": "CorrectPass123",
        "role": "student"
    })
    
    response = client.post("/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401

def test_password_validation(client):
    response = client.post("/auth/register", json={
        "name": "Weak Pass",
        "email": "weak@test.com",
        "password": "weak",
        "role": "student"
    })
    assert response.status_code == 422