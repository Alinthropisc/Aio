from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    driver: str = Field(default="postgresql+psycopg", alias="DB_DRIVER")
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    name: str = Field(default="aioback", alias="DB_NAME")
    user: str = Field(default="postgres", alias="DB_USER")
    password: str = Field(default="postgres", alias="DB_PASSWORD")

    pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    echo: bool = Field(default=False, alias="DB_ECHO")

    @property
    def url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}
