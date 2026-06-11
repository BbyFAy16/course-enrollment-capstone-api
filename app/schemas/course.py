from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    capacity: int = Field(..., gt=0, description="Course capacity must be greater than 0")

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class CourseResponse(CourseBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class CourseDetail(CourseResponse):
    enrolled_count: int = 0
    available_spots: int = 0
    
    @classmethod
    def from_course(cls, course, enrolled_count):
        return cls(
            id=course.id,
            title=course.title,
            code=course.code,
            capacity=course.capacity,
            is_active=course.is_active,
            enrolled_count=enrolled_count,
            available_spots=course.capacity - enrolled_count
        )

class CourseSearchParams(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    min_capacity: Optional[int] = None
    max_capacity: Optional[int] = None

class CourseStudentResponse(BaseModel):
    enrollment_id: int
    user_id: int
    name: str
    email: str
    enrolled_at: datetime