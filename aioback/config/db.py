from pydantic import Field

from core.config import BaseAppSettings


class DatabaseSettings(BaseAppSettings):
    """Настройки основной БД (PostgreSQL по умолчанию)."""

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


class SecondaryDatabaseSettings(BaseAppSettings):
    """Настройки второй БД (MySQL по умолчанию). Включается через SECONDARY_DB_ENABLED=true."""

    enabled: bool = Field(default=False, alias="SECONDARY_DB_ENABLED")
    driver: str = Field(default="mysql+aiomysql", alias="SECONDARY_DB_DRIVER")
    host: str = Field(default="localhost", alias="SECONDARY_DB_HOST")
    port: int = Field(default=3306, alias="SECONDARY_DB_PORT")
    name: str = Field(default="aioback", alias="SECONDARY_DB_NAME")
    user: str = Field(default="root", alias="SECONDARY_DB_USER")
    password: str = Field(default="", alias="SECONDARY_DB_PASSWORD")
    pool_size: int = Field(default=5, alias="SECONDARY_DB_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="SECONDARY_DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, alias="SECONDARY_DB_POOL_TIMEOUT")
    echo: bool = Field(default=False, alias="SECONDARY_DB_ECHO")

    @property
    def url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
