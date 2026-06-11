from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")