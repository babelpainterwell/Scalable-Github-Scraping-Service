"""
Through data access layer, the service layer interacts with the database. 
"""

from typing import List, Optional
from app.data_access.repositories.project_repository import ProjectRepository
from app.data_access.repositories.user_repository import UserRepository
from app.external_services.github_api import GitHubAPIClient
from app.models import Project, User
import logging 
from app.core.exceptions import NotFoundError, DatabaseError, ExternalAPIError

# get a logger for current module
logger = logging.getLogger(__name__)


class Service:
    @staticmethod 
    async def get_user_projects_service(username: str) -> Optional[List[Project]]:
        try:
            try: 
                user = await UserRepository.get_by_username(username)
            except DatabaseError as e:
                logger.error(f"Database error: {e}")
                raise DatabaseError("Error fetching user.")
            
            if user:
                try: 
                    projects = await ProjectRepository.get_by_user_id(user.id)
                except DatabaseError as e:
                    logger.error(f"Database error: {e}")
                    raise DatabaseError("Error fetching projects.")
                return projects
            else:
                github_client = GitHubAPIClient()
                try:
                    projects_data = await github_client.fetch_user_projects(username)
                    """
                    Needs to distinguish between user not found and user having no public repositories
                    1. if a user is not found, a NOT FOUND error should be raised
                    2. if a user is found but has no public repositories, no error should be raised
                    """
                    # projects_data could be empty if the user has no public repositories

                except NotFoundError as e:
                    logger.warning(f"User '{username}' not found in both database and on Github.")
                    raise NotFoundError(f"User '{username}' not found in database and on Github.")
                except ExternalAPIError as e:
                    logger.error(f"Error fetching projects from Github for user '{username}': {e}")
                    raise ExternalAPIError("Error fetching projects from Github.")
                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}")
                    raise
                finally:
                    await github_client.close()
                
                # Create user
                user = User(username=username)
                try: 
                    user = await UserRepository.create(user)
                except DatabaseError as e:
                    logger.error(f"Database error: {e}")
                    raise DatabaseError("Error creating user.")

                # Create projects (could be empty)
                try: 
                    projects = await ProjectRepository.create_projects(user.id, projects_data)
                except DatabaseError as e:
                    logger.error(f"Database error: {e}")
                    raise DatabaseError("Error creating projects.")
                return projects

        except NotFoundError as e:
            logger.warning(f"User '{username}' not found in database and on Github.")
            raise NotFoundError(f"User '{username}' not found in database and on Github.")
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError("Error fetching user or projects.")
        except ExternalAPIError as e:
            logger.error(f"External API error: {e}")
            raise ExternalAPIError("Error fetching projects from Github.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise Exception("An unexpected error occurred.")

    @staticmethod
    async def get_most_recent_users_service(n:int)->List[User]:
        try: 
            users = await UserRepository.get_most_recent(n)
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError("Error fetching most recent users.")
        return users

    @staticmethod
    async def get_most_starred_projects_service(n:int)->List[Project]:
        try:  
            projects = await ProjectRepository.get_most_starred(n)
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError("Error fetching most starred projects.")
        return projects



