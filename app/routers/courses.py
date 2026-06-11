from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.course import Course
from ..models.enrollment import Enrollment
from ..models.user import User
from ..schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseDetail, CourseSearchParams
from ..dependencies.auth import get_current_user, get_current_active_admin

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=dict)
def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in title or code"),
    db: Session = Depends(get_db)
):
    """Get all courses with pagination and filtering"""
    query = db.query(Course)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Course.is_active == is_active)
    else:
        # By default, show only active courses for non-admin users
        query = query.filter(Course.is_active == True)
    
    if search:
        query = query.filter(
            (Course.title.ilike(f"%{search}%")) | 
            (Course.code.ilike(f"%{search}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    courses = query.offset(skip).limit(limit).all()
    
    # Add enrollment count to each course
    result = []
    for course in courses:
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id
        ).count()
        result.append(CourseDetail(
            id=course.id,
            title=course.title,
            code=course.code,
            capacity=course.capacity,
            is_active=course.is_active,
            enrolled_count=enrolled_count
        ))
    
    return {
        "courses": result,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/available", response_model=List[CourseDetail])
def get_available_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get courses that have available spots"""
    courses = db.query(Course).filter(
        Course.is_active == True
    ).offset(skip).limit(limit).all()
    
    result = []
    for course in courses:
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id
        ).count()
        
        if enrolled_count < course.capacity:
            result.append(CourseDetail(
                id=course.id,
                title=course.title,
                code=course.code,
                capacity=course.capacity,
                is_active=course.is_active,
                enrolled_count=enrolled_count
            ))
    
    return result

@router.get("/count", response_model=dict)
def get_courses_count(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get total count of courses"""
    query = db.query(Course)
    if is_active is not None:
        query = query.filter(Course.is_active == is_active)
    
    total = query.count()
    return {"total": total, "is_active": is_active}

@router.get("/{course_id}", response_model=CourseDetail)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course by ID"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    enrolled_count = db.query(Enrollment).filter(
        Enrollment.course_id == course.id
    ).count()
    
    return CourseDetail(
        id=course.id,
        title=course.title,
        code=course.code,
        capacity=course.capacity,
        is_active=course.is_active,
        enrolled_count=enrolled_count
    )

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Create a new course (Admin only)"""
    # Check if course code already exists
    existing_course = db.query(Course).filter(Course.code == course.code).first()
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists"
        )
    
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Update a course (Admin only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    update_data = course_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Delete a course (Admin only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db.delete(course)
    db.commit()

@router.patch("/{course_id}/deactivate", response_model=CourseResponse)
def deactivate_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Deactivate a course (Admin only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course.is_active = False
    db.commit()
    db.refresh(course)
    return course

@router.patch("/{course_id}/activate", response_model=CourseResponse)
def activate_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Activate a course (Admin only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course.is_active = True
    db.commit()
    db.refresh(course)
    return course

@router.get("/{course_id}/students", response_model=List[dict])
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """Get all students enrolled in a specific course (Admin only)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).join(User).all()
    
    students = []
    for enrollment in enrollments:
        students.append({
            "enrollment_id": enrollment.id,
            "user_id": enrollment.user.id,
            "name": enrollment.user.name,
            "email": enrollment.user.email,
            "enrolled_at": enrollment.created_at.isoformat()
        })
    
    return students