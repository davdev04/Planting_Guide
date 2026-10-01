import logging
import os
import re
from datetime import datetime
from pathlib import Path

from agent.agent_state import AgentState
from settings import Settings
from utils.validation import normalise_planting_age, sanitise_name

logger = logging.getLogger(__name__)
agent_state = AgentState()
settings = Settings()

try:
    from langchain.agents import initialize_agent, Tool
except ImportError:  # pragma: no cover - dependency may be absent in some environments
    initialize_agent = None
    Tool = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - dependency may be absent in some environments
    ChatOpenAI = None


def _load_openai_api_key():
    token = os.getenv("OPENAI_API_KEY")
    if token:
        return token

    env_file = Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = [part.strip() for part in line.split("=", 1)]
            if key == "OPENAI_API_KEY":
                os.environ[key] = value.strip('"\'')
                return value.strip('"\'')
    return None


def _load_copilot_token():
    return _load_openai_api_key()


def _build_llm():
    token = _load_openai_api_key()
    if not token:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to the environment or .env file.")
    if ChatOpenAI is None:
        raise RuntimeError("langchain_openai is not installed.")

    try:
        return ChatOpenAI(model=settings.model_name, api_key=token)
    except TypeError:
        try:
            return ChatOpenAI(model_name=settings.model_name, api_key=token)
        except TypeError:
            try:
                return ChatOpenAI(model=settings.model_name)
            except TypeError:
                return ChatOpenAI()


def _lookup_plant(plant_id: int):
    from services.plant_service import PlantService

    return PlantService().get_plant(plant_id)


agent = None


def create_agent():
    global agent
    if agent is not None:
        return agent
    if initialize_agent is None or Tool is None:
        logger.warning("[single_agent] LangChain agent tools are unavailable.")
        return None

    tools = [
        Tool(
            name="lookup_plant",
            func=_lookup_plant,
            description="Retrieve a plant by ID.",
        )
    ]

    try:
        llm = _build_llm()
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent="zero-shot-react-description",
            max_iterations=settings.agent_max_iterations,
            verbose=True,
        )
        return agent
    except Exception as exc:
        logger.exception("[single_agent] Failed to create LangChain OpenAI agent: %s", exc)
        agent_state.record_error(exc)
        return None


def _extract_valid_date(raw_output: object) -> str | None:
    text = str(raw_output).strip()
    if not text:
        return None

    candidates = []
    for match in re.findall(r"\d{4}-\d{2}-\d{2}", text):
        candidates.append(match)

    if not candidates:
        return None

    for candidate in candidates:
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
            return candidate
        except ValueError:
            continue

    return None


def _sanitize_name(name: object) -> str:
    return sanitise_name(name)


def _normalize_planting_age(planting_age: object | None) -> str:
    return normalise_planting_age(planting_age)


def _fallback_planting_date(name: str, planting_age: str | None = None) -> str:
    base = sum(ord(ch) for ch in name) + (len(name) * 13)
    if planting_age is None or planting_age == "":
        planting_age = "seed"

    month = ((base + (len(planting_age) * 7)) % 12) + 1
    day = ((base + len(planting_age) * 3) % 27) + 1
    year = 2026
    return f"{year:04d}-{month:02d}-{day:02d}"


def suggest_planting_date(name: str, planting_age: str | None = None):
    name = _sanitize_name(name)
    planting_age = _normalize_planting_age(planting_age)

    input_data = {"name": name, "planting_age": planting_age}
    state_before = agent_state.__dict__.copy()
    logger.info(f"Agent input: {input_data}")
    logger.info(f"State before: {state_before}")

    try:
        active_agent = create_agent()
        if active_agent is None:
            raise RuntimeError("The LangChain OpenAI agent could not be started.")

        raw_input = f"Plant name: {name}. Planting age: {planting_age}. Suggest an optimal planting date for Brisbane, Australia in YYYY-MM-DD format only."
        raw_output = active_agent.run(raw_input)
        logger.info(f"Raw LLM output: {raw_output}")

        suggestion = _extract_valid_date(raw_output)
        if suggestion is None:
            agent_state.record_invalid_output(raw_output)
            raise ValueError(f"Invalid planting date output from agent: {raw_output!r}")

        agent_state.record_run()
        agent_state.set_last_suggestion(suggestion)
        agent_state.record(f"Suggested planting date for {name} ({planting_age}): {suggestion}")
        logger.info("[single_agent] AI suggestion stored in agent state: %s", agent_state.snapshot())
        logger.info(f"State after: {agent_state.__dict__}")
        return suggestion
    except Exception as exc:
        agent_state.record_error(exc)
        fallback = _fallback_planting_date(name, planting_age)
        agent_state.record_run()
        agent_state.set_last_suggestion(fallback)
        agent_state.record(f"Fallback suggestion for {name} ({planting_age}): {fallback}")
        logger.warning("[single_agent] Falling back to deterministic suggestion for %s (%s): %s", name, planting_age, fallback)
        logger.info(f"State after: {agent_state.__dict__}")
        return fallback


try:
    agent = create_agent()
except Exception:  # pragma: no cover - defensive fallback for import-time safety
    agent = None