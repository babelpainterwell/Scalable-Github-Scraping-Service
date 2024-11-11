from fastapi import FastAPI
from app.api.routes import router as api_router



app = FastAPI(title = "Github Scraper API")