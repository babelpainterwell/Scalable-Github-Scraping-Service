"""
sets up the database connection 
"""

# for making asynchrounous database connections
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True) # for debugging 


# session make factory 
# prevent the session from being closed after a commit for data reuse
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False 
) 

# Depends(get_db) allows FASTAPI to create a new session for each request
# async def get_db():
#     async with async_session() as session:
#         yield session