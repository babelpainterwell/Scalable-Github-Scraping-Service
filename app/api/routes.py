"""define api endpoints"""
from typing import List
from app.models.schemas import ProjectResponse, UserResponse

router = APIRouter()

@router.get("/users/{username}/projects ", response_model=List[ProjectResponse])