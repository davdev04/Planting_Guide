import pytest

import agent.single_agent as single_agent_module


def test_extract_valid_date_accepts_valid_iso_dates():
    assert single_agent_module._extract_valid_date("The best date is 2026-08-21.") == "2026-08-21"
    assert single_agent_module._extract_valid_date("2024-12-31 and 2025-01-01") == "2024-12-31"


def test_extract_valid_date_rejects_invalid_or_missing_dates():
    assert single_agent_module._extract_valid_date("Planting date: not-a-date") is None
    assert single_agent_module._extract_valid_date("") is None
    assert single_agent_module._extract_valid_date("No date here") is None


def test_fallback_planting_date_is_deterministic(monkeypatch):
    result = single_agent_module._fallback_planting_date("Rose", "seedling")

    assert result.startswith("2026-")
    assert len(result) == 10
    assert result == single_agent_module._fallback_planting_date("Rose", "seedling")


def test_sanitize_name_rejects_malicious_or_invalid_input():
    with pytest.raises(ValueError, match="invalid characters|unsupported characters"):
        single_agent_module._sanitize_name("Rose; rm -rf /")

    with pytest.raises(ValueError, match="required|too long"):
        single_agent_module._sanitize_name("   ")

    assert single_agent_module._sanitize_name("  Rose-123  ") == "Rose-123"


def test_normalize_planting_age_rejects_invalid_values():
    assert single_agent_module._normalize_planting_age("SEEDLING") == "seedling"
    assert single_agent_module._normalize_planting_age(None) == "seed"

    with pytest.raises(ValueError, match="must be 'seed' or 'seedling'"):
        single_agent_module._normalize_planting_age("unknown")


def test_suggest_planting_date_rejects_invalid_input_before_agent_run(monkeypatch):
    def fail_if_called():
        raise AssertionError("Agent should not run for invalid input")

    monkeypatch.setattr(single_agent_module, "create_agent", fail_if_called)

    with pytest.raises(ValueError, match="invalid characters|unsupported characters"):
        single_agent_module.suggest_planting_date("Rose; rm -rf /", "seedling")

    with pytest.raises(ValueError, match="must be 'seed' or 'seedling'"):
        single_agent_module.suggest_planting_date("Rose", "unknown")


def test_suggest_planting_date_uses_agent_output_when_valid(monkeypatch):
    class DummyAgent:
        def run(self, _):
            return "The best date is 2026-08-21."

    monkeypatch.setattr(single_agent_module, "create_agent", lambda: DummyAgent())
    monkeypatch.setattr(single_agent_module.agent_state, "record_run", lambda: None)
    monkeypatch.setattr(single_agent_module.agent_state, "set_last_suggestion", lambda suggestion: None)
    monkeypatch.setattr(single_agent_module.agent_state, "record", lambda event: None)
    monkeypatch.setattr(single_agent_module.agent_state, "record_error", lambda exc: None)
    monkeypatch.setattr(single_agent_module.agent_state, "record_invalid_output", lambda output: None)

    result = single_agent_module.suggest_planting_date("Rose", "seedling")

    assert result == "2026-08-21"


def test_suggest_planting_date_falls_back_when_invalid_output(monkeypatch):
    class DummyAgent:
        def run(self, _):
            return "Planting date: not-a-date"

    recorded = []

    monkeypatch.setattr(single_agent_module, "create_agent", lambda: DummyAgent())
    monkeypatch.setattr(single_agent_module.agent_state, "record_invalid_output", lambda output: recorded.append(output))
    monkeypatch.setattr(single_agent_module.agent_state, "record_error", lambda exc: recorded.append(str(exc)))
    monkeypatch.setattr(single_agent_module.agent_state, "record_run", lambda: None)
    monkeypatch.setattr(single_agent_module.agent_state, "set_last_suggestion", lambda suggestion: recorded.append(suggestion))
    monkeypatch.setattr(single_agent_module.agent_state, "record", lambda event: recorded.append(event))

    result = single_agent_module.suggest_planting_date("Rose", "seedling")

    assert result.startswith("2026-")
    assert len(result) == 10
    assert any("not-a-date" in str(item) for item in recorded)


def test_create_agent_returns_none_when_langchain_tools_unavailable(monkeypatch):
    monkeypatch.setattr(single_agent_module, "agent", None)
    monkeypatch.setattr(single_agent_module, "initialize_agent", None)
    monkeypatch.setattr(single_agent_module, "Tool", None)

    result = single_agent_module.create_agent()

    assert result is None


def test_create_agent_builds_agent_when_available(monkeypatch):
    class DummyTool:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class DummyAgent:
        pass

    def fake_build_llm():
        return object()

    monkeypatch.setattr(single_agent_module, "agent", None)
    monkeypatch.setattr(single_agent_module, "initialize_agent", lambda **kwargs: DummyAgent())
    monkeypatch.setattr(single_agent_module, "Tool", DummyTool)
    monkeypatch.setattr(single_agent_module, "_build_llm", fake_build_llm)

    result = single_agent_module.create_agent()

    assert isinstance(result, DummyAgent)
