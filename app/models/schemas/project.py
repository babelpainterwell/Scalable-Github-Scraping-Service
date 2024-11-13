from typing import Optional 
from pydantic import BaseModel 

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    stars: int 
    forks: int 

class ProjectCreate(ProjectBase):
    user_id: int 

class ProjectResponse(ProjectBase):
    id: int 
    user_id: int

    class Config:
        # suggested by CHATGPT to make the response model work with SQLAlchemy
        # Pydantic enforces strict data validation, ValidationError might be raised 
        orm_mode = True 
        
