"""
define api endpoints
"""


from fastapi import APIRouter
from typing import List
from app.models.schemas import ProjectResponse, UserResponse

router = APIRouter()

@router.get("/users/{username}/projects ", response_model=List[ProjectResponse])
async def get_user_projects(username: str):
    """
    retrieve projects for a give github user
    """
    pass

@router.get("users/recent/{n}", response_model= List[UserResponse])
async def get_most_recent_users(n: int):
    """
    get n most recent users saved in the database 
    """
    pass 

@router.get("projects/most-starred/{n}", response_model=List[ProjectResponse])
async def get_most_starred_projects(n: int):
    """
    get n most starred projects saved in the database
    """
    pass