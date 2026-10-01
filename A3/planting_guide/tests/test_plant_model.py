from models.plant import Plant
from datetime import date

def test_plant_model_defaults():
    plant = Plant(name="Test Plant")
    assert plant.name == "Test Plant"
    assert plant.planting_date is None
    assert plant.id is None

def test_plant_model_with_planting_date():
    scheduled = date(2025, 1, 1)
    plant = Plant(name="Scheduled Plant", planting_date=scheduled)
    assert plant.planting_date == scheduled