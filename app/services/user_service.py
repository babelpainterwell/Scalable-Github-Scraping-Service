"""
Through data access layer, the service layer interacts with the database. 
"""

from typing import List, Optional
from app.data_access.repositories.project_repository import ProjectRepository
from app.data_access.repositories.user_repository import UserRepository
from app.external_services.github_api import GitHubAPIClient
from app.models import Project, User
import logging 
from app.core.exceptions import NotFoundError, DatabaseError

# get a logger for current module
logger = logging.getLogger(__name__)


class Service:
    @staticmethod 
    async def get_user_projects_service(username: str) -> Optional[List[Project]]:
        try:
            user = await UserRepository.get_by_username(username)
            if user:
                projects = await ProjectRepository.get_by_user_id(user.id)
                return projects
            else:
                github_client = GitHubAPIClient()
                try:
                    pass
                except Exception as e:
                    logger.error(f"Error fetching projects from Github for user {username}: {e}")
                    raise 
        except:






async def get_user_projects(username:str) -> Optional[List[ProjectResponse]]:
    """
    1. check if the user exists in the database 
    2. if not, fetches projects from Github and saves them.
    3. returns a list of ProjectResponse objects
    4. handles exceptions
    """
    try:
        user = await UserRepository.get_by_username(username)
        if user:
            projects = await ProjectRepository.get_by_user_id(user.id)
        else:
            github_client = GitHubAPIClient()
            try: 
                projects_data = await github_client.fetch_user_projects(username)
            except Exception as e:
                return None # User not found on Github
            finally:
                await github_client.close()
            # save the user and their projects
            user = await UserRepository.create(username)
            projects = await ProjectRepository.create_projects(user.id, projects_data)
        # return projcts, convert ORM models to Pydantic models
        return [ProjectResponse.from_orm(project) for project in projects]

    except Exception as e:
        # log the exception 
        return None
