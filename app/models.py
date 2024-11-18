# app/models.py

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # make sure it's autoincremented
    name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="projects")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True) # for faster lookups
    created_at: datetime = Field(default_factory=datetime.utcnow)
    projects: List[Project] = Relationship(back_populates="user")
