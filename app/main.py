from fastapi import FastAPI
from app.api.routes import router as api_router
import logging
from app.core.logging_config import *



app = FastAPI(title = "Github Scraper API")