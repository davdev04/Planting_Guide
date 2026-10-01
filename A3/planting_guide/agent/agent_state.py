import logging

logger = logging.getLogger(__name__)


class AgentState:
    def __init__(self):
        self.last_suggestion = None
        self.error_count = 0
        self.history = []
        self.total_runs = 0
        self.invalid_outputs = 0
        self._log_state("initialized")

    def record(self, event: str):
        self.history.append(event)
        self._log_state(event)

    def record_run(self):
        self.total_runs += 1
        self.history.append(f"run: {self.total_runs}")
        self._log_state("run_recorded")

    def record_invalid_output(self, output=None):
        self.invalid_outputs += 1
        self.history.append(f"invalid_output: {output}")
        logger.warning("[AgentState] Invalid output recorded: %s", output)
        self._log_state("invalid_output_recorded")

    def set_last_suggestion(self, suggestion):
        self.last_suggestion = suggestion
        self.history.append(f"last_suggestion: {suggestion}")
        self._log_state("last_suggestion_updated")

    def record_error(self, error):
        self.error_count += 1
        message = str(error)
        self.history.append(f"error: {message}")
        logger.error("[AgentState] Agent error recorded: %s", message)
        self._log_state("error_recorded")

    def snapshot(self):
        return {
            "last_suggestion": self.last_suggestion,
            "error_count": self.error_count,
            "total_runs": self.total_runs,
            "invalid_outputs": self.invalid_outputs,
            "history": list(self.history),
        }

    def _log_state(self, event: str):
        logger.info("[AgentState] %s state=%s", event, self.snapshot())