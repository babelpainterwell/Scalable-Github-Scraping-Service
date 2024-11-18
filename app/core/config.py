
# app/core/config.py
# ConfigDict is suggested by CHATGPT to load environment variables from the .env file.

from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # An async SQLite driver is needed
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Use ConfigDict to load environment variables from the .env file
    model_config = ConfigDict(env_file=".env")

settings = Settings()
