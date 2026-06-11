from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .user import UserResponse
from .course import CourseResponse

class EnrollmentCreate(BaseModel):
    course_id: int = Field(..., gt=0, description="Course ID to enroll in")

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    user: Optional[UserResponse] = None
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True

class EnrollmentDetail(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    course_title: Optional[str] = None
    course_code: Optional[str] = None
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    
    class Config:
        from_attributes = True

class EnrollmentList(BaseModel):
    enrollments: List[EnrollmentResponse]
    total: int
    skip: int
    limit: int

class EnrollmentStats(BaseModel):
    total_enrollments: int
    total_courses: int
    total_students: int
    average_enrollments_per_course: float