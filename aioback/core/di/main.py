from dishka import AsyncContainer, make_async_container

from .app import InfraProvider, SettingsProvider
from .cache import CacheProvider
from .db import DatabaseProvider
from .queue import QueueProvider


def build_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DatabaseProvider(),
        CacheProvider(),
        InfraProvider(),
        QueueProvider(),
    )
