# app/services/user_service.py
# Create a user service that will be used to interact with the repositories and external services.


import logging 
from app.core.logging_config import *
from typing import List, Optional
from app.data_access.repositories.project_repository import ProjectRepository
from app.data_access.repositories.user_repository import UserRepository
from app.external_services.github_api import GitHubAPIClient
from app.models import Project, User
from app.core.exceptions import NotFoundError, DatabaseError, ExternalAPIError

# get a logger for current module
logger = logging.getLogger(__name__)


class Service:

    @staticmethod
    async def get_user_projects_service(username: str) -> List[Project]:
        try:
            user = await UserRepository.get_by_username(username)
            if user:
                projects = await ProjectRepository.get_by_user_id(user.id)
                return projects
            else:
                github_client = GitHubAPIClient()
                """
                    Needs to distinguish between user not found and user having no public repositories
                    1. if a user is not found, a NOT FOUND error should be raised
                    2. if a user is found but has no public repositories, no error should be raised
                """
                projects_data = await github_client.fetch_user_projects(username)
                await github_client.close()

                # Create user
                user = User(username=username)
                user = await UserRepository.create(user)

                # Create projects (could be empty)
                projects = []
                if projects_data:
                    projects = await ProjectRepository.create_projects(user.id, projects_data)

                return projects  # Can be empty list
        except NotFoundError:
            logger.warning(f"User '{username}' not found on GitHub.")
            raise NotFoundError(f"User '{username}' not found on GitHub.")
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError("Error fetching user or projects.")
        except ExternalAPIError as e:
            logger.error(f"External API error: {e}")
            raise ExternalAPIError("Error fetching projects from GitHub.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise 


    @staticmethod
    async def get_most_recent_users_service(n:int)->List[User]:
        try: 
            users = await UserRepository.get_most_recent(n)
            return users
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError("Error fetching most recent users.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise 
        

    @staticmethod
    async def get_most_starred_projects_service(n:int)->List[Project]:
        try:  
            projects = await ProjectRepository.get_most_starred(n)
            return projects
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError("Error fetching most starred projects.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise 
        



