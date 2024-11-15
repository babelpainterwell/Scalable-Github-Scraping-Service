"""
create a project repository that will be used to interact with the database
"""

from app.data_access.database import async_session
from app.models import Project
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from sqlmodel import select
import logging



logger = logging.getLogger(__name__)

class ProjectRepository:
    @staticmethod
    async def get_most_starred(n: int) -> Optional[List[Project]]:
        """
        Get n most starred projects
        """
        try:
            async with async_session() as session:
                statement = select(Project).order_by(Project.stars.desc()).limit(n)
                result = await session.execute(statement)
                return result.scalars().all()
        except SQLAlchemyError as e:
            return []
        

    @staticmethod 
    async def get_by_user_id(user_id: int) -> Optional[List[Project]]:
        """
        Get all projects by user id
        """
        try:
            async with async_session() as session:
                statement = select(Project).where(Project.user_id == user_id)
                result = await session.execute(statement)
                return result.scalars().all()
        except SQLAlchemyError as e:
            return []
    
    @staticmethod
    async def create_projects(user_id: int, projects_data: List[dict]) -> Optional[List[Project]]:
        """
        Create projects for a user.
        """
        try:
            async with async_session() as session:
                projects = []
                for data in projects_data:
                    project = Project(
                        name=data['name'],
                        description=data.get('description'),
                        stars=data.get('stargazers_count', 0),
                        forks=data.get('forks_count', 0),
                        user_id=user_id
                    )
                    session.add(project)
                    projects.append(project)
                await session.commit()
                return projects
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_projects: {e}")
            return []