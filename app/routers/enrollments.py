from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.course import Course
from ..models.enrollment import Enrollment
from ..models.user import User, UserRole
from ..schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentDetail
from ..dependencies.auth import get_current_user, get_current_active_student, get_current_active_admin

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.get("/stats", response_model=dict)
def get_enrollment_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get enrollment statistics (Admin only)"""
    total_enrollments = db.query(Enrollment).count()
    total_courses = db.query(Course).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    
    avg_enrollments_per_course = total_enrollments / total_courses if total_courses > 0 else 0
    
    return {
        "total_enrollments": total_enrollments,
        "total_courses": total_courses,
        "total_students": total_students,
        "average_enrollments_per_course": round(avg_enrollments_per_course, 2)
    }

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_active_student)
):
    """Enroll the current student in a course"""
    # Check if course exists
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if course is active
    if not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot enroll in an inactive course"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_student.id,
        Enrollment.course_id == enrollment.course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Check course capacity
    enrolled_count = db.query(Enrollment).filter(
        Enrollment.course_id == enrollment.course_id
    ).count()
    
    if enrolled_count >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course is full. Capacity: {course.capacity}, Enrolled: {enrolled_count}"
        )
    
    # Create enrollment
    db_enrollment = Enrollment(
        user_id=current_student.id,
        course_id=enrollment.course_id
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def deregister_from_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_active_student)
):
    """Deregister the current student from a course"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_student.id,
        Enrollment.course_id == course_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    db.delete(enrollment)
    db.commit()

@router.get("/me", response_model=List[EnrollmentDetail])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_active_student)
):
    """Get all enrollments for the current student"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_student.id
    ).all()
    
    return [
        EnrollmentDetail(
            id=e.id,
            user_id=e.user_id,
            course_id=e.course_id,
            created_at=e.created_at,
            course_title=e.course.title,
            course_code=e.course.code
        ) for e in enrollments
    ]

@router.get("/check/{course_id}", response_model=dict)
def check_enrollment_status(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if the current user is enrolled in a specific course"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    
    return {
        "enrolled": enrollment is not None,
        "course_id": course_id,
        "user_id": current_user.id,
        "enrollment_id": enrollment.id if enrollment else None
    }

@router.get("/admin/all", response_model=List[EnrollmentResponse])
def get_all_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all enrollments (Admin only)"""
    enrollments = db.query(Enrollment).offset(skip).limit(limit).all()
    return enrollments

@router.get("/admin/course/{course_id}", response_model=List[EnrollmentDetail])
def get_course_enrollments(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all enrollments for a specific course (Admin only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    return [
        EnrollmentDetail(
            id=e.id,
            user_id=e.user_id,
            course_id=e.course_id,
            created_at=e.created_at,
            course_title=e.course.title,
            course_code=e.course.code,
            student_name=e.user.name,
            student_email=e.user.email
        ) for e in enrollments
    ]

@router.get("/admin/user/{user_id}", response_model=List[EnrollmentDetail])
def get_user_enrollments(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all enrollments for a specific user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == user_id
    ).all()
    
    return [
        EnrollmentDetail(
            id=e.id,
            user_id=e.user_id,
            course_id=e.course_id,
            created_at=e.created_at,
            course_title=e.course.title,
            course_code=e.course.code,
            student_name=user.name,
            student_email=user.email
        ) for e in enrollments
    ]

@router.delete("/admin/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_remove_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Remove an enrollment (Admin only)"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    db.delete(enrollment)
    db.commit()