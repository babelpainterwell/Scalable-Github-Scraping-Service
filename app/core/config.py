"""
create a settings class that can be used to store configuration settings for the entire application
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # an async sqlite driver is needed
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # to load environment variables from the .env file 
    class Config:
        env_file = ".env"

settings = Settings()