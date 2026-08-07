from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Monday BI Agent"
    APP_VERSION: str = "1.0.0"

    MONDAY_API_TOKEN: str
    OPENAI_API_KEY: str

    CACHE_TTL: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()