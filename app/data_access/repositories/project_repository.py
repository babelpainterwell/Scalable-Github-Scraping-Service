"""
create a project repository that will be used to interact with the database
"""

from app.data_access.database import async_session


class ProjectRepository:
    @staticmethod
    async def get_most_starred(n: int):
        """
        get n most starred projects
        """
        pass

    @staticmethod 
    async def get_by_user_id(user_id: int):
        """
        get all projects by user id
        """
        pass

    @staticmethod
    async def create_projects(user_id: int, projects_data: dict):
        """
        create projects for a user
        """
        pass