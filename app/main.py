# app/main.py


import logging
from app.core.logging_config import *
from fastapi import FastAPI, HTTPException, Request
from app.api.routes import router as api_router
from app.data_access.database import engine
from sqlmodel import SQLModel
from app.core.exceptions import NotFoundError, DatabaseError, ExternalAPIError
from fastapi.responses import JSONResponse



app = FastAPI(title = "Github Scraper API")
app.include_router(api_router)



@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# cannot directly call synchronous methods using an async engion

# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)




# THE CODE BELOW IS GENERATED BY CHATGPT.
# THE CODE BELOW IS GENERATED BY CHATGPT.
# THE CODE BELOW IS GENERATED BY CHATGPT.

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found."}
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."}
    )

@app.exception_handler(ExternalAPIError)
async def external_api_exception_handler(request: Request, exc: ExternalAPIError):
    return JSONResponse(
        status_code=503,
        content={"detail": "External API error."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )
