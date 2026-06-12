from dishka import Provider, Scope, provide

from config import AppSettings, BotSettings, DatabaseSettings, RedisSettings, SecondaryDatabaseSettings, Settings
from core.security import PasswordHasher
from core.utils import FileManager


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        from config import get_settings

        return get_settings()

    @provide(scope=Scope.APP)
    def get_app_settings(self, s: Settings) -> AppSettings:
        return s.app

    @provide(scope=Scope.APP)
    def get_db_settings(self, s: Settings) -> DatabaseSettings:
        return s.db

    @provide(scope=Scope.APP)
    def get_secondary_db_settings(self, s: Settings) -> SecondaryDatabaseSettings:
        return s.secondary_db

    @provide(scope=Scope.APP)
    def get_redis_settings(self, s: Settings) -> RedisSettings:
        return s.redis

    @provide(scope=Scope.APP)
    def get_bot_settings(self, s: Settings) -> BotSettings:
        return s.bot


class InfraProvider(Provider):
    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def get_file_manager(self) -> FileManager:
        return FileManager(base_dir="storage")
