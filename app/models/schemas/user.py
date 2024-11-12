from pydantic import BaseModel 
from typing import List 
from datetime import datetime

class UserBase(BaseModel):
    username: str 

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int 
    created_at: datetime

    class Config:
        orm_mode = True