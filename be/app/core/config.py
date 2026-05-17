from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Market Trend API"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    NAVER_DATALAB_CLIENT_ID: str = ""
    NAVER_DATALAB_CLIENT_SECRET: str = ""

    KIS_APP_KEY: str = ""
    KIS_APP_SECRET: str = ""
    KIS_BASE_URL: str = "https://openapi.koreainvestment.com:9443"

    DB_HOST: str = Field(default="localhost", alias="HOST")
    DB_PORT: int = Field(default=5432, alias="PORT")
    DB_NAME: str = Field(default="market", alias="DATABASE")
    DB_USER: str = Field(default="admin", alias="USER")
    DB_PASSWORD: str = Field(default="", alias="PASSWORD")

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str) and value.lower() in {"release", "production", "prod"}:
            return False
        return value

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
