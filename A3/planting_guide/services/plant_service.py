import logging

from agent.single_agent import suggest_planting_date as suggest_date
from models.plant import Plant
from utils.validation import normalise_planting_age, sanitise_name

logger = logging.getLogger(__name__)


def suggest_planting_date(name: str, planting_age=None):
    return suggest_date(name, planting_age)


class PlantService:
    def __init__(self):
        self.plants: list[Plant] = []
        self.counter = 1

    def create_plant(self, name: str, planting_date=None, planting_age=None) -> int:
        """Create a plant and return its assigned id."""
        try:
            safe_name = sanitise_name(name)
            safe_age = normalise_planting_age(planting_age)

            plant = Plant(
                id=None,
                name=safe_name,
                planting_date=planting_date,
                planting_age=safe_age,
            )

            plant.id = self.counter
            self.counter += 1

            if plant.planting_date is None:
                suggested = suggest_planting_date(plant.name, plant.planting_age)
                if suggested:
                    plant.planting_date = suggested
                    logger.info("[PlantService] Planting date suggested: %s", suggested)

            self.plants.append(plant)
            logger.info(
                "[PlantService] Created plant",
                extra={
                    "plant_id": plant.id,
                    "plant_name": plant.name,
                    "planting_age": plant.planting_age,
                    "planting_date": str(plant.planting_date) if plant.planting_date else None,
                },
            )
            return plant.id
        except Exception as exc:
            logger.exception("[PlantService] Error creating plant: %s", exc)
            raise

    def get_plant(self, plant_id: int) -> Plant:
        """Return the plant with the given id or raise KeyError if missing."""
        found = next((p for p in self.plants if p.id == plant_id), None)
        if not found:
            raise KeyError("Plant not found")
        return found

    def list_plants(self) -> list[Plant]:
        """Return a copy of all plants."""
        return list(self.plants)

    def delete_plant(self, plant_id: int) -> None:
        try:
            plant = self.get_plant(plant_id)
            self.plants.remove(plant)
            logger.info("[PlantService] Deleted plant", extra={"plant_id": plant_id, "plant_name": plant.name})
            return None
        except KeyError:
            logger.warning("[PlantService] Error deleting plant: plant not found (%s)", plant_id)
            raise
        except Exception as exc:
            logger.exception("[PlantService] Error deleting plant %s: %s", plant_id, exc)
            raise