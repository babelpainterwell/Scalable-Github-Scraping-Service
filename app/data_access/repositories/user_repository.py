"""
create a user repository that will be used to interact with the database
"""

from app.data_access.database import async_session
from app.models import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import select
from typing import Optional, List
import logging
from app.core.exceptions import DatabaseError


logger = logging.getLogger(__name__)


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
                # it should't retrieve more than one user and could be None
                user = result.scalars().one_or_none() 

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
            logger.error(f"User repository error in get_by_username: {e}")
            raise DatabaseError("SQLAlchemyError fetching user by username.")
        except Exception as e:
            logger.error(f"An unexpected user repository error occurred: {e}")
            raise DatabaseError("Error fetching user by username.")

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
        except IntegrityError as e:
            # ensure user uniqueness
            logger.error(f"User repository integrity error in create: {e}")
            raise DatabaseError("User already exists.")
        except SQLAlchemyError as e:
            logger.error(f"User repository error in create: {e}")
            raise DatabaseError("SQLAlchemyError creating user.")
        except Exception as e:
            logger.error(f"An unexpected user repository error occurred: {e}")
            raise DatabaseError("Error creating user.")

    @staticmethod
    async def get_most_recent(n: int) -> List[User]:
        """
        Retrieve the n most recent users, ordered by creation date, which could be empty.
        """
        try:
            async with async_session() as session:
                statement = select(User).order_by(User.created_at.desc()).limit(n)
                result = await session.execute(statement)
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"User repository error in get_most_recent: {e}")
            raise DatabaseError("SQLAlchemyError fetching most recent users.")
        except Exception as e:
            raise DatabaseError("Error fetching most recent users.")