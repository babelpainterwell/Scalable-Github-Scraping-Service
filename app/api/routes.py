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
    1. if the user is not in the database, fetches the user's projects from the Github API
        a. if the user is not found on Github, the service should raise a NotFoundError
        b. if the user is found on Github but has no public repositories, the api should raise a NotFoundError
    2. if the user is in the database, fetches the user's projects from the database
        a. if the user has no projects in the database, the api should raise a NotFoundError
        b. if the user has projects in the database, the api should return the projects
    3. Allow other errors to propagate from the service such as DatabaseError and ExternalAPIError
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
    1. if there are no users in the database, the api should raise a NotFoundError
    2. Allow other errors to propagate from the service such as DatabaseError
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
    1. if there are no projects in the database, the api should raise a NotFoundError
    2. Allow other errors to propagate from the service such as DatabaseError
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


