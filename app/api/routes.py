"""
define api endpoints
"""


from fastapi import APIRouter, HTTPException
from typing import List
from app.models import User, Project
from app.services.user_service import Service
from app.core.exceptions import NotFoundError, DatabaseError, ExternalAPIError

router = APIRouter()

@router.get("/users/{username}/projects", response_model=List[Project])
async def get_user_projects(username:str):
    """
    fetches projects for a given user.
    """
    try:
        projects = await Service.get_user_projects_service(username)
        if not projects:
            raise NotFoundError(status_code=404, detail="No projects found for user.")
        return projects
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/users/recent/{n}", response_model=List[User])
async def get_most_recent_users(n:int):
    """
    retrieve the n most recent users
    """
    try:
        users = await Service.get_most_recent_users_service(n)
        if not users:
            raise NotFoundError(status_code=404, detail="No users found.")
        return users
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/projects/most-starred/{n}", response_model=List[Project])
async def get_most_starred_projects(n:int):
    """
    retrieve the n most starred projects
    """
    try:
        projects = await Service.get_most_starred_projects_service(n)
        if not projects:
            raise NotFoundError(status_code=404, detail="No projects found.")
        return projects
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


