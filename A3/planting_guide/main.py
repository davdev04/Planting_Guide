"""Application entrypoint for the Planting Guide API."""

import logging
from settings import settings
from fastapi import FastAPI
from api.fast_api import router as plant_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(title="Planting Guide API")
app.include_router(plant_router)
