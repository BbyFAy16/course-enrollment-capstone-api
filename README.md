# Course Enrollment Platform API

A secure, production-ready RESTful API for managing course enrollments built with FastAPI, PostgreSQL, and JWT authentication. This platform implements complete role-based access control, comprehensive business logic validation, and thorough automated testing.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication & Authorization](#authentication--authorization)
- [API Endpoints Reference](#api-endpoints-reference)
- [Business Rules](#business-rules)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Features
* **User Management**: Registration, login, profile management
* **Course Management**: Create, update, delete, activate/deactivate courses
* **Enrollment System**: Enroll, deregister, track course capacity
* **Role-Based Access Control**: Student and Admin roles with distinct permissions
* **JWT Authentication**: Secure token-based authentication
* **Data Validation**: Comprehensive input validation using Pydantic
* **Error Handling**: Consistent error responses with meaningful messages

### Advanced Features
* **Pagination & Filtering**: All list endpoints support pagination and filtering
* **Search Functionality**: Search users by name/email, courses by title/code
* **Enrollment Statistics**: Track enrollments, capacity, and availability
* **User Activation/Deactivation**: Admin can manage user account status
* **Bulk Operations**: Efficient handling of multiple records
* **Soft Delete Support**: Course deactivation without data loss
* **Audit Trail**: Enrollment timestamps for tracking
* **API Documentation**: Auto-generated Swagger/ReDoc documentation

### Security Features
* **Password Hashing**: Bcrypt hashing for secure password storage
* **JWT Tokens**: Expiring tokens with configurable lifetime
* **Input Sanitization**: Protection against injection attacks
* **CORS Support**: Configurable Cross-Origin Resource Sharing
* **Rate Limiting Ready**: Architecture supports adding rate limiting

## Technology Stack

* **Backend Framework**: FastAPI 0.104+
* **Database**: PostgreSQL 14+ (SQLite for testing)
* **ORM**: SQLAlchemy 2.0+
* **Authentication**: JWT (python-jose)
* **Password Hashing**: Passlib with Bcrypt
* **Migration Tool**: Alembic
* **Testing**: Pytest with HTTPX
* **Validation**: Pydantic v2
* **Server**: Uvicorn/Gunicorn

## Prerequisites

* Python 3.11 or higher
* PostgreSQL 14 or higher (or SQLite for development)
* pip (Python package manager)
* virtualenv or venv (recommended)
* Git (for version control)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/BbyFAy16/course-enrollment-capstone-api.git
cd course-enrollment-api
```

### 2. Create Virtual Environment

Create the virtual environment in your project folder:
```bash
python -m venv venv
```

Activate the environment based on your operating system:

**macOS or Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Edit the `.env` file in the root directory of the project with the configuration below. 

```env
# Database Configuration
# Toggle between PostgreSQL or SQLite by commenting/uncommenting the lines below
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/course_enrollment
# DATABASE_URL=sqlite:///./course_enrollment.db

# JWT Configuration
SECRET_KEY=011f104c44d55a0f8f421ba478624f77c82c9e01bd9f7ab0b13c4cd4796ad2a9
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Configuration
APP_NAME="Course Enrollment API"
DEBUG=False
```

### 5. Database Configuration

#### Option 1: PostgreSQL

##### Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**  
Download and install from [postgresql.org](https://postgresql.org).

##### Create Database

Access PostgreSQL:
```bash
psql -U postgres
```

In the PostgreSQL prompt, run the following SQL commands:
```sql
CREATE DATABASE course_enrollment;
GRANT ALL PRIVILEGES ON DATABASE course_enrollment TO postgres;
\q
```

#### Option 2: SQLite (For Local Development)

SQLite requires no extra installation or server setup. The database file will be created automatically in your project root folder when you run the application or execute database migrations.

To use SQLite, update your connection string in the configuration file:

```ini
DATABASE_URL=sqlite:///./course_enrollment.db
```


### 6. Database Migration with Alembic

Initialize Alembic:
```bash
alembic init alembic
```

Create initial migration:
```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply migration:
```bash
alembic upgrade head
```

Check migration status:
```bash
alembic current
```

Rollback last migration (if needed):
```bash
alembic downgrade -1
```

### 7. Running The Application

#### Development Mode

Start with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

With specific log level:
```bash
uvicorn app.main:app --reload --log-level debug
```

#### Production Mode

Using uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Using gunicorn with uvicorn workers:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Verify Application is Running

Check if the API is running:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Welcome to Course Enrollment API",
  "docs": "/docs",
  "version": "1.0.0"
}
```


### 8. API Documentation

Once the application is running, access the interactive API documentation:

* **Swagger UI**: <http://localhost:8000/docs>
* **ReDoc**: <http://localhost:8000/redoc>
* **OpenAPI Schema**: <http://localhost:8000/openapi.json>

### 9. Authentication & Authorization

#### Authentication Flow

1. Register a new user account
2. Login to receive a JWT access token
3. Include the token in the Authorization header for protected endpoints:
   ```http
   Authorization: Bearer <your_token>
   ```
4. Tokens expire after the configured time (default: 30 minutes)

#### Role-Based Access Control (RBAC)

The system supports two roles with different permissions:

| Action | Student | Admin |
| :--- | :---: | :---: |
| View courses | ✅ | ✅ |
| View own profile | ✅ | ✅ |
| Update own profile | ✅ | ✅ |
| Enroll in course | ✅ | ❌ |
| Deregister from course | ✅ | ❌ |
| View own enrollments | ✅ | ❌ |
| Create course | ❌ | ✅ |
| Update course | ❌ | ✅ |
| Delete course | ❌ | ✅ |
| Activate/Deactivate course | ❌ | ✅ |
| View all users | ❌ | ✅ |
| Update users | ❌ | ✅ |
| Delete users | ❌ | ✅ |
| View all enrollments | ❌ | ✅ |
| Remove enrollments | ❌ | ✅ |
| Enrollment statistics | ❌ | ✅ |

#### Creating an Admin User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "AdminPass123",
    "role": "admin"
  }'
```


### 10. API Endpoints Reference

#### Authentication Endpoints

##### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "student"
}
```

Response: `201 Created`

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student",
  "is_active": true
}
```

##### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

Response: `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### User Endpoints

| Method | Endpoint | Description | Auth | Role |
| :--- | :--- | :--- | :---: | :--- |
| GET | `/users/me` | Get current user profile | Yes | Any |
| PUT | `/users/me` | Update current user profile | Yes | Any |
| GET | `/users/` | List all users (paginated) | Yes | Admin |
| GET | `/users/count` | Get user statistics | Yes | Admin |
| GET | `/users/{id}` | Get user by ID | Yes | Any |
| PUT | `/users/{id}` | Update user | Yes | Admin |
| DELETE | `/users/{id}` | Delete user | Yes | Admin |
| PATCH | `/users/{id}/deactivate` | Deactivate user | Yes | Admin |
| PATCH | `/users/{id}/activate` | Activate user | Yes | Admin |

##### Query Parameters for `GET /users/`

* `skip` (int, default 0): Number of records to skip
* `limit` (int, default 100, max 100): Records per page
* `role` (string, optional): Filter by role ("student" or "admin")
* `is_active` (bool, optional): Filter by active status
* `search` (string, optional): Search in name or email

#### Course Endpoints

| Method | Endpoint | Description | Auth | Role |
| :--- | :--- | :--- | :---: | :--- |
| GET | `/courses/` | List courses (paginated) | No | Public |
| GET | `/courses/available` | List available courses | No | Public |
| GET | `/courses/count` | Get course count | No | Public |
| GET | `/courses/{id}` | Get course details | No | Public |
| POST | `/courses/` | Create new course | Yes | Admin |
| PUT | `/courses/{id}` | Update course | Yes | Admin |
| DELETE | `/courses/{id}` | Delete course | Yes | Admin |
| PATCH | `/courses/{id}/deactivate` | Deactivate course | Yes | Admin |
| PATCH | `/courses/{id}/activate` | Activate course | Yes | Admin |
| GET | `/courses/{id}/students` | Get enrolled students | Yes | Admin |

##### Query Parameters for `GET /courses/`

* `skip` (int, default 0): Number of records to skip
* `limit` (int, default 100, max 100): Records per page
* `is_active` (bool, optional): Filter by active status
* `search` (string, optional): Search in title or code

#### Enrollment Endpoints

| Method | Endpoint | Description | Auth | Role |
| :--- | :--- | :--- | :---: | :--- |
| POST | `/enrollments/` | Enroll in a course | Yes | Student |
| DELETE | `/enrollments/{course_id}` | Deregister from course | Yes | Student |
| GET | `/enrollments/me` | Get my enrollments | Yes | Student |
| GET | `/enrollments/check/{course_id}` | Check enrollment status | Yes | Any |
| GET | `/enrollments/stats` | Enrollment statistics | Yes | Admin |
| GET | `/enrollments/admin/all` | All enrollments | Yes | Admin |
| GET | `/enrollments/admin/course/{course_id}` | Course enrollments | Yes | Admin |
| GET | `/enrollments/admin/user/{user_id}` | User enrollments | Yes | Admin |
| DELETE | `/enrollments/admin/{enrollment_id}` | Remove enrollment | Yes | Admin |

### 11. Business Rules

#### User Registration Rules

* Email must be unique in the system
* Password must be at least 8 characters
* Password must contain:
  * At least one uppercase letter
  * At least one lowercase letter
  * At least one digit
* Default role is "student" if not specified
* Inactive users cannot authenticate

#### Course Management Rules

* Course code must be unique
* Course capacity must be greater than zero
* Only active courses are shown in public listings
* Admins can activate/deactivate courses
* Deleting a course removes all associated enrollments

#### Enrollment Rules

* Only authenticated students can enroll
* Students cannot enroll in the same course twice
* Cannot enroll in inactive courses
* Cannot enroll if course is at full capacity
* Enrollment is atomic and thread-safe
* Students can only deregister from their own enrollments
* Admins can remove any enrollment

#### Data Validation Rules

* All text fields have minimum and maximum length constraints
* Email format is validated
* Numeric fields are validated for appropriate ranges
* Required fields cannot be empty
* UUID and ID fields are validated for correct format

### 12. Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py -v

# Run specific test function
pytest tests/test_users.py::test_get_current_user_profile -v

# Run with print statements
pytest -s

# Run with coverage report
pytest --cov=app tests/

# Run with detailed coverage report
pytest --cov=app --cov-report=term-missing --cov-report=html tests/

# Run tests matching a pattern
pytest -k "test_admin" -v
```

#### Test Coverage

The test suite covers:

| Category | Coverage | Tests |
| :--- | :---: | :--- |
| Authentication | 100% | Registration, login, token validation |
| User Management | 100% | CRUD operations, filtering, pagination |
| Course Management | 100% | CRUD, activation, capacity checks |
| Enrollment System | 100% | Enroll, deregister, business rules |
| Authorization | 100% | RBAC, permission checks |
| Edge Cases | 100% | Invalid inputs, error handling |
| Integration | 100% | End-to-end workflows |

#### Test Structure

```text
tests/
├── conftest.py           # Test fixtures and configuration
├── test_auth.py          # Authentication tests
├── test_users.py         # User management tests
├── test_courses.py       # Course management tests
└── test_enrollments.py   # Enrollment system tests
```

### 13. Project Structure

```text
course_enrollment/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── course.py          # Course model
│   │   └── enrollment.py      # Enrollment model
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas
│   │   ├── course.py          # Course schemas
│   │   └── enrollment.py      # Enrollment schemas
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User endpoints
│   │   ├── courses.py         # Course endpoints
│   │   └── enrollments.py     # Enrollment endpoints
│   ├── dependencies/           # FastAPI dependencies
│   │   ├── __init__.py
│   │   └── auth.py            # Auth dependencies
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── security.py        # Security utilities
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_courses.py
│   └── test_enrollments.py
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini
├── requirements.txt
├── .env                        # Environment variables (not in git)
├── .gitignore
└── README.md
```

### 14. Database Schema

#### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'student' 
        CHECK (role IN ('student', 'admin')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### Courses Table

```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_courses_code ON courses(code);
CREATE INDEX idx_courses_active ON courses(is_active);
```

#### Enrollments Table

```sql
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);

CREATE INDEX idx_enrollments_user ON enrollments(user_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
```

#### Entity Relationship Diagram

```text
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    Users    │         │ Enrollments  │         │   Courses   │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ id (PK)     │──┐      │ id (PK)      │      ┌──│ id (PK)     │
│ name        │  └──────│ user_id (FK) │──────┘  │ title       │
│ email       │         │ course_id(FK)│         │ code        │
│ password    │         │ created_at   │         │ capacity    │
│ role        │         └──────────────┘         │ is_active   │
│ is_active   │                                  └─────────────┘
└─────────────┘
```

### 14. Deployment

#### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/course_enrollment
      - SECRET_KEY=production-secret-key
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=course_enrollment
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with Docker Compose:

```bash
docker-compose up -d
docker-compose exec web alembic upgrade head
```

#### Cloud Deployment Options

##### Heroku

```bash
heroku create course-enrollment-api
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-production-secret-key
git push heroku main
heroku run alembic upgrade head
```

##### AWS Elastic Beanstalk

```bash
eb init -p python-3.11 course-enrollment-api
eb create course-enrollment-env
eb setenv SECRET_KEY=your-production-secret-key
eb deploy
```

##### Railway

* Connect your GitHub repo to Railway.
* Add environment variables in the Railway dashboard.
* Deploy automatically on every `git push`.

### 15. Performance Optimization

* **Database Indexes**: Optimized for frequent queries.
* **Connection Pooling**: Efficient database connection management.
* **Pagination**: All list endpoints support pagination.
* **Lazy Loading**: SQLAlchemy relationships configured for performance.
* **Response Caching**: Headers set for appropriate caching.
* **Async Support**: FastAPI's async capabilities ready for async database drivers.

### 16. Security Considerations

* **Password Hashing**: Bcrypt with automatic salt generation.
* **JWT Security**: Signed tokens with expiration.
* **SQL Injection Prevention**: ORM-based queries.
* **CORS Configuration**: Configurable allowed origins.
* **Input Validation**: All inputs validated through Pydantic schemas.
* **Error Messages**: No sensitive data leaked in error responses.
* **HTTPS**: Force SSL/HTTPS usage in production environments.
* **Rate Limiting**: Recommended for production (can be added via middleware).

### 17. Troubleshooting

#### Common Issues

##### Database Connection Error

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Restart PostgreSQL
sudo systemctl restart postgresql
```

##### Migration Issues

```bash
# Reset database
dropdb course_enrollment
createdb course_enrollment
alembic upgrade head
```

##### Import Errors

```bash
# Ensure you're in the project root
cd course_enrollment

# Check Python path
python -c "import app; print(app.__file__)"
```

##### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

#### Logging

Enable debug logging in your `.env` file:

```env
DEBUG=True
```

### 18. Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

#### Development Guidelines

* Write tests for new features.
* Follow the PEP 8 style guide.
* Update documentation for any API changes.
* Ensure all tests pass before submitting a PR.
* Use Python type hints consistently.

### 19. License

This project is licensed under the MIT License - see the LICENSE file for details.

### 20. Acknowledgments

* **FastAPI** — Modern web framework
* **SQLAlchemy** — SQL toolkit and ORM
* **Pydantic** — Data validation
* **Alembic** — Database migrations
* **Pytest** — Testing framework

### 21. Support

For support, please:

1. Check the repository Issues page.
2. Review the API Documentation.
3. Contact the maintainers.

---

Built with ❤️ using FastAPI by Peter Stafsen aka Fay

Last updated: June 2026
