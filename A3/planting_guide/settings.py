from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    log_level: str = "INFO"
    agent_max_iterations: int = 5


settings = Settings()