from functools import lru_cache

from .app import AppSettings
from .bot import BotSettings
from .db import DatabaseSettings
from .redis import RedisSettings


class Settings:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.db = DatabaseSettings()
        self.redis = RedisSettings()
        self.bot = BotSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
