"""Plant models for the planting guide API."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Age(str, Enum):
    """Plant age when planted."""

    seed = "seed"
    seedling = "seedling"


class Plant(BaseModel):
    """Represents a plant with a name, planting age, recommended planting date and ID."""

    id: Optional[int] = Field(None, description="Unique identifier for the plant.")
    name: str = Field(..., description="The plant name.")
    planting_date: Optional[date] = Field(None, description="The recommended planting date for the plant.")
    planting_age: Optional[Age] = Field(None, description="The age when planted.")
