import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, "..", ".env")


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path)
    POSTGRES_DB: str = Field(alias="POSTGRES_DB", description="postgre's db")
    POSTGRES_HOST: str = Field(alias="POSTGRES_HOST", description="postgre's host")
    POSTGRES_USER: str = Field(alias="POSTGRES_USER", description="postgre's user")
    POSTGRES_PASSWORD: str = Field(
        alias="POSTGRES_PASSWORD", description="postgre's password"
    )
    POSTGRES_PORT: int = Field(
        default=5432,
        alias="POSTGRES_PORT",
        description="postgre's port",
        ge=0,
        le=65535,
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


config = Config()  # type: ignore
