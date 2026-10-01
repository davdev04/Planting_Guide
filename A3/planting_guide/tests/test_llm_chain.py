import os

import pytest

import utils.llm_chain as llm_chain_module


def test_load_openai_api_key_uses_environment_variable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "env-token")

    assert llm_chain_module._load_openai_api_key() == "env-token"


def test_load_openai_api_key_reads_dotenv_file(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    env_dir = tmp_path / "project"
    env_dir.mkdir()
    env_file = env_dir / ".env"
    env_file.write_text('OPENAI_API_KEY="file-token"\nOTHER=value\n')

    utils_dir = env_dir / "utils"
    utils_dir.mkdir()
    fake_module_path = utils_dir / "llm_chain.py"
    fake_module_path.write_text("placeholder")

    monkeypatch.setattr(llm_chain_module, "__file__", str(fake_module_path))

    token = llm_chain_module._load_openai_api_key()

    assert token == "file-token"
    assert os.environ["OPENAI_API_KEY"] == "file-token"


def test_build_openai_llm_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(llm_chain_module, "_load_openai_api_key", lambda: None)
    monkeypatch.setattr(llm_chain_module, "ChatOpenAI", object)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is missing"):
        llm_chain_module._build_openai_llm()


def test_build_openai_llm_uses_api_key_and_model(monkeypatch):
    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    calls = []

    def fake_loader():
        calls.append("loader")
        return "abc-token"

    monkeypatch.setattr(llm_chain_module, "_load_openai_api_key", fake_loader)
    monkeypatch.setattr(llm_chain_module, "ChatOpenAI", DummyClient)

    llm = llm_chain_module._build_openai_llm()

    assert isinstance(llm, DummyClient)
    assert llm.kwargs["model"] == llm_chain_module.settings.model_name
    assert llm.kwargs["api_key"] == "abc-token"
    assert calls == ["loader"]


def test_build_openai_llm_falls_back_to_model_name_kwarg(monkeypatch):
    class DummyClient:
        def __init__(self, *args, **kwargs):
            if "model" in kwargs and "api_key" in kwargs:
                raise TypeError("model + api_key unsupported")
            self.kwargs = kwargs

    monkeypatch.setattr(llm_chain_module, "_load_openai_api_key", lambda: "fallback-token")
    monkeypatch.setattr(llm_chain_module, "ChatOpenAI", DummyClient)

    llm = llm_chain_module._build_openai_llm()

    assert llm.kwargs["model_name"] == llm_chain_module.settings.model_name
    assert llm.kwargs["api_key"] == "fallback-token"


def test_build_openai_llm_uses_default_constructor_when_supported(monkeypatch):
    class DummyClient:
        def __init__(self, *args, **kwargs):
            if args or kwargs:
                raise TypeError("unexpected args")
            self.created = True

    monkeypatch.setattr(llm_chain_module, "_load_openai_api_key", lambda: "default-token")
    monkeypatch.setattr(llm_chain_module, "ChatOpenAI", DummyClient)

    llm = llm_chain_module._build_openai_llm()

    assert isinstance(llm, DummyClient)
    assert llm.created is True
