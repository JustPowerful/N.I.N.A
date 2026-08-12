from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str | None = None # API key for OPENAI (or compatible OPENAI API)
    openai_base_url: str | None = None # Base URL for OPENAI (or compatible OPENAI API)
    model: str = "nvidia/nemotron-3.5-lightning:free" # default model (you can change it later)


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()

if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

if not settings.openai_base_url:
    raise ValueError("OPENAI_BASE_URL is not set in the environment variables.")