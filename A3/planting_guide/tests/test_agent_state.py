import agent.agent_state as agent_state_module
from agent.agent_state import AgentState


def test_agent_state_initializes_with_defaults_and_logs(monkeypatch):
    calls = []

    def fake_info(*args, **kwargs):
        calls.append(args)

    monkeypatch.setattr(agent_state_module.logger, "info", fake_info)

    state = AgentState()

    assert state.last_suggestion is None
    assert state.error_count == 0
    assert state.history == []
    assert state.total_runs == 0
    assert state.invalid_outputs == 0
    assert any(len(call) >= 3 and call[0] == "[AgentState] %s state=%s" and call[1] == "initialized" for call in calls)
    assert state.snapshot()["history"] == []


def test_record_run_updates_counts_and_history(monkeypatch):
    calls = []

    def fake_info(*args, **kwargs):
        calls.append(args)

    monkeypatch.setattr(agent_state_module.logger, "info", fake_info)

    state = AgentState()
    state.record_run()

    assert state.total_runs == 1
    assert state.history[-1] == "run: 1"
    assert state.snapshot()["total_runs"] == 1
    assert any(len(call) >= 3 and call[0] == "[AgentState] %s state=%s" and call[1] == "run_recorded" for call in calls)


def test_record_invalid_output_increments_counter_and_history(monkeypatch):
    warnings = []

    def fake_warning(*args, **kwargs):
        warnings.append(args)

    monkeypatch.setattr(agent_state_module.logger, "warning", fake_warning)
    monkeypatch.setattr(agent_state_module.logger, "info", lambda *args, **kwargs: None)

    state = AgentState()
    state.record_invalid_output("Planting date: not-a-date")

    assert state.invalid_outputs == 1
    assert state.history[-1] == "invalid_output: Planting date: not-a-date"
    assert state.snapshot()["invalid_outputs"] == 1
    assert any("Invalid output recorded" in str(warning[0]) for warning in warnings)


def test_set_last_suggestion_updates_last_suggestion_and_history(monkeypatch):
    calls = []

    def fake_info(*args, **kwargs):
        calls.append(args)

    monkeypatch.setattr(agent_state_module.logger, "info", fake_info)

    state = AgentState()
    state.set_last_suggestion("2026-08-21")

    assert state.last_suggestion == "2026-08-21"
    assert state.history[-1] == "last_suggestion: 2026-08-21"
    assert state.snapshot()["last_suggestion"] == "2026-08-21"
    assert any(len(call) >= 3 and call[0] == "[AgentState] %s state=%s" and call[1] == "last_suggestion_updated" for call in calls)


def test_record_error_increments_error_count_and_history(monkeypatch):
    errors = []

    def fake_error(*args, **kwargs):
        errors.append(args)

    monkeypatch.setattr(agent_state_module.logger, "error", fake_error)
    monkeypatch.setattr(agent_state_module.logger, "info", lambda *args, **kwargs: None)

    state = AgentState()
    state.record_error("Agent failed")

    assert state.error_count == 1
    assert state.history[-1] == "error: Agent failed"
    assert state.snapshot()["error_count"] == 1
    assert any("Agent error recorded" in str(error[0]) for error in errors)
