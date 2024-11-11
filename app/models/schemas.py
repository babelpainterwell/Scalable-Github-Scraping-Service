from typing import Optional 
from pydantic import BaseModel 
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str]
    stars: int 
    forks: int 

class ProjectCreate(ProjectBase):
    user_id: int 

class ProjectResponse(ProjectBase):
    id: int 
    user_id: int

    class Config:
        orm_mode = True # suggested by CHATGPT to make the response model work with SQLAlchemy

class UserBase(BaseModel):
    username: str 

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int 
    created_at: datetime

    class Config:
        orm_mode = True