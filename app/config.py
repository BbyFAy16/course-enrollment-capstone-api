from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://course_569l_user:7rPGWZdd1SoI19r584gliHOT5hRR9KBv@dpg-dac1d62jnfac73el39sg-a.frankfurt-postgres.render.com/course_569l"
    
    # JWT
    SECRET_KEY: str = "011f104c44d55a0f8f421ba478624f77c82c9e01bd9f7ab0b13c4cd4796ad2a9"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "Course Enrollment API"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
