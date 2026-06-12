from dishka.integrations.litestar import setup_dishka
from litestar import Litestar

from config import get_settings
from core.di import build_container
from core.logging import Log
from listeners.registry import ListenerRegistry
from middleware import LoggingMiddleware, RequestIdMiddleware
from routes.api import get_routes


def create_app() -> Litestar:
    settings = get_settings()
    Log.setup(debug=settings.app.is_debug, env=settings.app.env)

    ListenerRegistry().register()

    app = Litestar(
        route_handlers=get_routes(),
        middleware=[
            RequestIdMiddleware,
            LoggingMiddleware,
        ],
        debug=settings.app.is_debug,
    )

    container = build_container()
    setup_dishka(container, app)

    return app


app = create_app()
