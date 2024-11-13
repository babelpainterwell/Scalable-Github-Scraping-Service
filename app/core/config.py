"""
I leverage the BaseSettings class from pydantic to create a settings class 
that can be used to store configuration settings for the application.
"""

from pydantic import BaseSettings

class Settings(BaseSettings):
    # could be overridden in the .env file
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    GITHUB_API_TOKEN: str = ""

    # to load environment variables from the .env file 
    class Config:
        env_file = ".env"

settings = Settings()