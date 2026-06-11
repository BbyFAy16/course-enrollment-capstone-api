def test_get_active_courses(client, test_course):
    response = client.get("/courses/")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert courses[0]["is_active"] == True

def test_get_course_by_id(client, test_course):
    response = client.get(f"/courses/{test_course.id}")
    assert response.status_code == 200
    assert response.json()["code"] == "TEST101"

def test_create_course_as_admin(client, admin_token):
    response = client.post(
        "/courses/",
        json={
            "title": "New Course",
            "code": "NEW101",
            "capacity": 25
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["code"] == "NEW101"

def test_create_course_as_student(client, student_token):
    response = client.post(
        "/courses/",
        json={
            "title": "Student Course",
            "code": "STU101",
            "capacity": 25
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403

def test_create_course_duplicate_code(client, admin_token, test_course):
    response = client.post(
        "/courses/",
        json={
            "title": "Another Course",
            "code": "TEST101",  # Same code as test_course
            "capacity": 30
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

def test_update_course(client, admin_token, test_course):
    response = client.put(
        f"/courses/{test_course.id}",
        json={"title": "Updated Course"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Course"

def test_delete_course(client, admin_token, test_course):
    response = client.delete(
        f"/courses/{test_course.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204