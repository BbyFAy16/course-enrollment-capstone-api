def test_enroll_in_course(client, student_token, test_course):
    response = client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 201
    assert response.json()["course_id"] == test_course.id

def test_double_enrollment(client, student_token, test_course):
    # First enrollment
    client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Second enrollment attempt
    response = client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 400
    assert "Already enrolled" in response.json()["detail"]

def test_enroll_full_course(client, test_course, db):
    from app.models.user import User, UserRole
    from app.utils.security import get_password_hash
    
    # Create course with capacity 2
    test_course.capacity = 2
    db.commit()
    
    # Create and enroll 2 students
    for i in range(2):
        student = User(
            name=f"Student {i}",
            email=f"student{i}@test.com",
            hashed_password=get_password_hash("TestPass123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(student)
        db.commit()
        
        # Login and enroll
        login_response = client.post("/auth/login", json={
            "email": f"student{i}@test.com",
            "password": "TestPass123"
        })
        token = login_response.json()["access_token"]
        
        client.post(
            "/enrollments/",
            json={"course_id": test_course.id},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Create third student
    student3 = User(
        name="Student 3",
        email="student3@test.com",
        hashed_password=get_password_hash("TestPass123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(student3)
    db.commit()
    
    login_response = client.post("/auth/login", json={
        "email": "student3@test.com",
        "password": "TestPass123"
    })
    token = login_response.json()["access_token"]
    
    # Try to enroll (should fail)
    response = client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Course is full" in response.json()["detail"]

def test_enroll_inactive_course(client, student_token, test_course, db):
    test_course.is_active = False
    db.commit()
    
    response = client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 400
    assert "inactive" in response.json()["detail"]

def test_deregister_from_course(client, student_token, test_course):
    # Enroll first
    client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Deregister
    response = client.delete(
        f"/enrollments/{test_course.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 204

def test_admin_view_enrollments(client, admin_token, student_token, test_course):
    # Enroll a student first
    client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    # Admin views enrollments
    response = client.get(
        f"/enrollments/admin/course/{test_course.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_admin_remove_enrollment(client, admin_token, student_token, test_course):
    # Enroll student
    enrollment_response = client.post(
        "/enrollments/",
        json={"course_id": test_course.id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    enrollment_id = enrollment_response.json()["id"]
    
    # Admin removes enrollment
    response = client.delete(
        f"/enrollments/admin/{enrollment_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204