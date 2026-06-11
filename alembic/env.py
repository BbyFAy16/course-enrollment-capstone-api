import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.config import get_settings

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata