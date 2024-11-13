"""
create a user repository that will be used to interact with the database
"""

from app.data_access.database import async_session
from app.models import User
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from typing import Optional, List


class UserRepository:
    @staticmethod
    async def get_by_username(username: str) -> Optional[User]:
        """
        Retrieve a user by their username.
        """
        try:
            async with async_session() as session:
                statement = select(User).where(User.username == username)
                result = await session.execute(statement)
                user = result.one_or_none()  # it should't retrieve more than one user

                """
                Even though I haven't implemented an auto-refresh mechanism for this project to synchronize the user's latest projects into the database, 
                to better mimic real-world scenarios where the database data might change after the object was initially queried, 
                I refresh the object to get its latest state. 
                The 'session.refresh()' method seems an effective way to ensure the data is up-to-date at the end of the query.
                """
                if user:
                    await session.refresh(user, attribute_names=["projects"])
                return user
        except SQLAlchemyError as e:
            # Log the exception here
            return None

    @staticmethod
    async def create(user: User) -> Optional[User]:
        """
        Create a new user and commit to the database.
        """
        try: 
            async with async_session() as session:
                session.add(user)
                await session.commit()
                return user
        except SQLAlchemyError as e:
            # Log the exception here
            return None

    @staticmethod
    async def get_most_recent(n: int) -> List[User]:
        """
        Retrieve the n most recent users, ordered by creation date.
        """
        try:
            async with async_session() as session:
                statement = select(User).order_by(User.created_at.desc()).limit(n)
                result = await session.exec(statement)
                return result.scalars().all()
        except SQLAlchemyError as e:
            # Log the exception here
            return []