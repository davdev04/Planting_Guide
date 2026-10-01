import pytest
from fastapi.testclient import TestClient
from main import app
from services.plant_service import PlantService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def fresh_service():
    # Create a fresh PlantService instance for isolated tests
    return PlantService()