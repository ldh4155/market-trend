from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Market Trend API"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    class Config:
        env_file = ".env"


settings = Settings()
