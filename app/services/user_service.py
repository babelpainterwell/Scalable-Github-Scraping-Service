"""
Through data access layer, the service layer interacts with the database. 
"""

from typing import List, Optional
from app.models.schemas.project import ProjectResponse, UserResponse
from app.data_access.repositories.project_repository import ProjectRepository
from app.data_access.repositories.user_repository import UserRepository

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
        # return projcts START HERE!!!
    except SQLAlchemyError as e:
        # log the exception 
        return None
