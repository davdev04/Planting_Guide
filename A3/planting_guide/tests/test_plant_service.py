import logging
import time
from datetime import date

import pytest

import services.plant_service as plant_service_module
from agent.single_agent import suggest_planting_date
from models.plant import Plant


def test_agent_rejects_invalid_date_output(monkeypatch):
    class DummyAgent:
        def run(self, _):
            return "Planting date: not-a-date"

    monkeypatch.setattr("agent.single_agent.create_agent", lambda: DummyAgent())

    result = suggest_planting_date("Rose", "seedling")

    assert result.startswith("2026-")
    assert len(result) == 10


def test_agent_accepts_valid_date_output(monkeypatch):
    class DummyAgent:
        def run(self, _):
            return "The best date is 2026-08-21."

    monkeypatch.setattr("agent.single_agent.create_agent", lambda: DummyAgent())

    result = suggest_planting_date("Rose", "seedling")

    assert result == "2026-08-21"


def test_agent_endpoint_times_out(client, monkeypatch):
    def slow_agent(name, planting_age=None):
        time.sleep(0.2)
        return "2026-08-21"

    monkeypatch.setattr("api.fast_api.agent_suggest_planting_date", slow_agent)
    monkeypatch.setattr("api.fast_api.AGENT_TIMEOUT_SECONDS", 0.05)

    response = client.post(
        "/api/agent/suggest_planting_date",
        json={"name": "Rose", "planting_age": "seedling"},
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "Planting date suggestion timed out."


def test_create_plant_logs_success(fresh_service, monkeypatch, caplog):
    monkeypatch.setattr(plant_service_module, "suggest_planting_date", lambda name, planting_age="seed": date(2026, 9, 30))

    with caplog.at_level(logging.INFO):
        plant_id = fresh_service.create_plant(
            "Test Plant",
            planting_age="seed",
        )

    assert plant_id == 1
    assert any("[PlantService] Created plant" in record.message for record in caplog.records)
    assert any("plant_id" in record.__dict__ and record.__dict__["plant_id"] == 1 for record in caplog.records)


def test_create_plant_assigns_id_and_stores_plant(fresh_service, monkeypatch):
    monkeypatch.setattr(plant_service_module, "suggest_planting_date", lambda title, planting_age="seedling": date(2026, 9, 30))

    plant_id = fresh_service.create_plant(
        "Test Plant",
        planting_age="seedling",
    )

    assert plant_id == 1
    assert len(fresh_service.plants) == 1
    plant = fresh_service.plants[0]
    assert plant.id == 1
    assert plant.name == "Test Plant"
    assert plant.planting_age == "seedling"
    assert plant.planting_date == date(2026, 9, 30)


def test_create_plant_keeps_explicit_values_without_ai_override(fresh_service):
    plant_id = fresh_service.create_plant(
        name="Test plant",
        planting_date=date(2026, 10, 15),
        planting_age="seed",
    )

    plant = fresh_service.get_plant(plant_id)
    assert plant.planting_date == date(2026, 10, 15)
    assert plant.planting_age == "seed"

def test_delete_plant_removes_existing_plant(fresh_service):
    plant_id = fresh_service.create_plant("Delete me")

    fresh_service.delete_plant(plant_id)

    assert len(fresh_service.plants) == 0
    assert all(plant.id != plant_id for plant in fresh_service.plants)


def test_delete_plant_logs_success(fresh_service, caplog):
    plant_id = fresh_service.create_plant("Delete me")

    with caplog.at_level(logging.INFO):
        fresh_service.delete_plant(plant_id)

    assert any("[PlantService] Deleted plant" in record.message for record in caplog.records)
    assert any(record.__dict__.get("plant_id") == plant_id for record in caplog.records)


def test_delete_plant_raises_keyerror_for_missing_plant(fresh_service):
    with pytest.raises(KeyError, match="Plant not found"):
        fresh_service.delete_plant(999)


def test_get_plant_returns_created_plant(fresh_service):
    plant_id = fresh_service.create_plant("Readable plant")

    found = fresh_service.get_plant(plant_id)

    assert isinstance(found, Plant)
    assert found.name == "Readable plant"
    assert found.id == plant_id

