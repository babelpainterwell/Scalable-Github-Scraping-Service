# app/api/routes.py - define the API routes
# ALL EXCEPTIONS WILL BE CAUGHT BY THE EXCEPTION HANDLERS IN THE MAIN.PY FILE


from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.models import User, Project
from app.services.user_service import Service
from app.core.exceptions import NotFoundError, DatabaseError, ExternalAPIError

router = APIRouter()

@router.get("/users/{username}/projects", response_model=List[Project])
async def get_user_projects(
    username: str = Path(..., pattern=r"^[a-zA-Z0-9-]{1,39}$", description="GitHub username")
):
    """
    fetches projects for a given user.
    1. if the user is not in the database, fetches the user's projects from the Github API
        a. if the user is not found on Github, the service should raise a NotFoundError
        b. if the user is found on Github but has no public repositories, the api should return an empty list
    2. if the user is in the database, fetches the user's projects from the database
        a. if the user has no projects in the database, the api should return an empty list
        b. if the user has projects in the database, the api should return the projects
    3. Allow other errors to propagate from the service such as DatabaseError and ExternalAPIError
    """
    projects = await Service.get_user_projects_service(username)
    # Do not raise NotFoundError for empty project lists!!!
    return projects


@router.get("/users/recent/{n}", response_model=List[User])
async def get_most_recent_users(
    n: int = Path(..., gt=0, le=100, description="Number of recent users to retrieve")
):
    """
    retrieve the n most recent users
    1. if there are no users in the database, the api should return an empty list
    2. Allow other errors to propagate from the service such as DatabaseError
    """
    users = await Service.get_most_recent_users_service(n)
    return users


@router.get("/projects/most-starred/{n}", response_model=List[Project])
async def get_most_starred_projects(
    n: int = Path(..., gt=0, le=100, description="Number of most starred projects to retrieve")
):
    """
    retrieve the n most starred projects
    1. if there are no projects in the database, the api should return an empty list
    2. Allow other errors to propagate from the service such as DatabaseError
    """
    projects = await Service.get_most_starred_projects_service(n)
    # Do not raise NotFoundError for empty project lists!!!
    return projects

