from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
class Settings(BaseSettings):
    openai_api_key: str = Field(default=...)
    openai_base_url: str = Field(default=...)
    
    model: str = "nvidia/nemotron-3.5-lightning:free" # default model (you can change it later)
    embedding_model: str = "nvidia/nemotron-3-embed-1b:free" # default model (you can change it later)

    # database related stuff
    database_url: str = Field(default=...)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()

