from pydantic import Field

from core.config import BaseAppSettings


class RedisSettings(BaseAppSettings):
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    password: str | None = Field(default=None, alias="REDIS_PASSWORD")
    max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")
    decode_responses: bool = Field(default=True, alias="REDIS_DECODE_RESPONSES")

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
