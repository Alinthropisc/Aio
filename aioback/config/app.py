from pydantic import Field

from core.config import BaseAppSettings


class AppSettings(BaseAppSettings):
    name: str = Field(default="aioback", alias="APP_NAME")
    version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    env: str = Field(default="development", alias="APP_ENV")

    host: str = Field(default="0.0.0.0", alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")
    workers: int = Field(default=1, alias="APP_WORKERS")

    allowed_origins: list[str] = Field(default=["*"], alias="APP_ALLOWED_ORIGINS")

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_debug(self) -> bool:
        return self.debug
