import os
from pathlib import Path

from agent.prompt import template
from settings import Settings

settings = Settings()

try:
    from langchain_classic.chains import LLMChain
except ImportError:  # pragma: no cover - optional dependency
    LLMChain = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency
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


def _build_openai_llm():
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


def _build_copilot_llm():
    return _build_openai_llm()


chain = None
if LLMChain is not None:
    try:
        chain = LLMChain(llm=_build_openai_llm(), prompt=template)
    except Exception:  # pragma: no cover - defensive fallback for missing credentials or package
        chain = None