import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.course import Course
from app.utils.security import get_password_hash

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    with TestClient(app) as c:
        yield c

@pytest.fixture
def student_token(client, db):
    # Create a student user
    student = User(
        name="Test Student",
        email="student@test.com",
        hashed_password=get_password_hash("TestPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    # Login to get token
    response = client.post("/auth/login", json={
        "email": "student@test.com",
        "password": "TestPass123"
    })
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client, db):
    # Create an admin user
    admin = User(
        name="Test Admin",
        email="admin@test.com",
        hashed_password=get_password_hash("AdminPass123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Login to get token
    response = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "AdminPass123"
    })
    return response.json()["access_token"]

@pytest.fixture
def test_course(db):
    course = Course(
        title="Test Course",
        code="TEST101",
        capacity=30,
        is_active=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course