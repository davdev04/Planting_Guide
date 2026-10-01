"""Plant API routes."""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agent.single_agent import suggest_planting_date as agent_suggest_planting_date
from models.plant import Age, Plant
from services.plant_service import PlantService

router = APIRouter()
plant_service = PlantService()
AGENT_TIMEOUT_SECONDS = 10.0


class PlantInput(BaseModel):
    """Payload for asking the AI for a planting date suggestion."""

    name: str = Field(..., description="The plant name.")
    planting_age: Optional[Age] = Field(None, description="The planting age for the plant.")


class PlantCreate(BaseModel):
    """Payload for creating a plant."""

    name: str = Field(..., description="The plant name.")
    planting_date: Optional[date] = Field(None, description="The optional planting date for the plant.")
    planting_age: Optional[Age] = Field(None, description="The planting age for the plant.")


@router.post("/api/agent/suggest_planting_date", tags=["agent"])
async def suggest_planting_date(plant: PlantInput):
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(agent_suggest_planting_date, plant.name, plant.planting_age),
            timeout=AGENT_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Planting date suggestion timed out.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate planting date suggestion.",
        ) from exc

    return {"suggested_planting_date": result}


@router.post("/plants", status_code=status.HTTP_201_CREATED, tags=["plants"])
def create_plant(payload: PlantCreate) -> dict[str, object]:
    """Create a new plant."""
    plant_id = plant_service.create_plant(
        name=payload.name,
        planting_date=payload.planting_date,
        planting_age=payload.planting_age,
    )
    return {"id": plant_id, "plant": plant_service.get_plant(plant_id)}


@router.get("/plants", response_model=list[Plant], tags=["plants"])
def list_plants() -> list[Plant]:
    """Return all plants."""
    return plant_service.list_plants()


@router.get("/plants/{plant_id}", response_model=Plant, tags=["plants"])
def get_plant(plant_id: int) -> Plant:
    """Return a plant by ID."""
    try:
        return plant_service.get_plant(plant_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found") from exc


@router.delete("/plants/{plant_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["plants"])
def delete_plant(plant_id: int) -> None:
    """Delete a plant by ID."""
    try:
        plant_service.delete_plant(plant_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found") from exc
    return None

