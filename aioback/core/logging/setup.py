import functools
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from loguru import logger

LOG_DIR = Path("storage/logs")

_FMT_CONSOLE = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
    "{exception}"
)
_FMT_FILE = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} | {message} | {extra}"


# ── Singleton конфигуратор ────────────────────────────────────────────────────


class _LoggingConfigurator:
    _configured: bool = False

    def configure(self, debug: bool = False, env: str = "development") -> None:
        if self._configured:
            return
        logger.remove()
        level = "DEBUG" if debug else "INFO"
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        logger.add(
            sys.stdout,
            level=level,
            format=_FMT_CONSOLE,
            colorize=True,
            enqueue=True,
            backtrace=True,
            diagnose=debug,
        )
        logger.add(
            LOG_DIR / "app.log",
            level=level,
            format=_FMT_FILE,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            encoding="utf-8",
            backtrace=True,
            diagnose=False,
        )
        logger.add(
            LOG_DIR / "error.log",
            level="ERROR",
            format=_FMT_FILE,
            rotation="10 MB",
            retention="90 days",
            compression="zip",
            enqueue=True,
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )
        if env == "production":
            logger.add(
                LOG_DIR / "critical.log",
                level="CRITICAL",
                format=_FMT_FILE,
                rotation="5 MB",
                retention="180 days",
                compression="zip",
                enqueue=True,
                encoding="utf-8",
            )

        import warnings

        warnings.showwarning = _warn_to_loguru
        sys.excepthook = _excepthook

        self._configured = True
        logger.info(f"Logging ready | level={level} | env={env}")


_configurator = _LoggingConfigurator()


# ── Decorator паттерн ─────────────────────────────────────────────────────────


def log_call(
    level: str = "DEBUG",
    log_args: bool = False,
    log_result: bool = False,
    catch: bool = True,
):
    def decorator(func: Callable) -> Callable:
        name = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            _log = logger.opt(depth=1)
            msg = f"→ {name}"
            if log_args:
                msg += f" | args={args[1:]} kwargs={kwargs}"
            _log.log(level, msg)
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                out = f"← {name} | {elapsed:.1f}ms"
                if log_result:
                    out += f" | result={result}"
                _log.log(level, out)
                return result
            except Exception as exc:
                elapsed = (time.perf_counter() - start) * 1000
                _log.error(f"✗ {name} | {elapsed:.1f}ms | {type(exc).__name__}: {exc}")
                if not catch:
                    raise
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            _log = logger.opt(depth=1)
            msg = f"→ {name}"
            if log_args:
                msg += f" | args={args[1:]} kwargs={kwargs}"
            _log.log(level, msg)
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                out = f"← {name} | {elapsed:.1f}ms"
                if log_result:
                    out += f" | result={result}"
                _log.log(level, out)
                return result
            except Exception as exc:
                elapsed = (time.perf_counter() - start) * 1000
                _log.error(f"✗ {name} | {elapsed:.1f}ms | {type(exc).__name__}: {exc}")
                if not catch:
                    raise
                raise

        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# ── Context Object паттерн ────────────────────────────────────────────────────


class RequestLogger:
    """
    async with RequestLogger("GET", "/users", request_id="abc") as log:
        log.info("inside request")
    """

    def __init__(self, method: str, path: str, request_id: str = "", **extra: Any) -> None:
        self._log = logger.bind(method=method, path=path, request_id=request_id, **extra)
        self._method = method
        self._path = path
        self._start = 0.0

    async def __aenter__(self):
        self._start = time.perf_counter()
        self._log.info(f"→ {self._method} {self._path}")
        return self._log

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self._start) * 1000
        if exc_type:
            self._log.error(f"✗ {self._method} {self._path} | {elapsed:.1f}ms | {exc_type.__name__}: {exc_val}")
        else:
            self._log.info(f"← {self._method} {self._path} | {elapsed:.1f}ms")
        return False


# ── Перехватчики ──────────────────────────────────────────────────────────────


def _warn_to_loguru(message, category, filename, lineno, file=None, line=None):
    logger.warning(f"{category.__name__}: {message} ({filename}:{lineno})")


def _excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logger.opt(exception=(exc_type, exc_value, exc_tb)).critical(f"Uncaught exception: {exc_type.__name__}")


# ── Facade паттерн — единая точка входа ──────────────────────────────────────


class Log:
    """
    Facade для всей системы логирования.
    Скрывает loguru, конфигуратор, декоратор и контекстный менеджер
    за одним простым интерфейсом.

    Использование:
        # Настройка (один раз при старте)
        Log.setup(debug=True, env="development")

        # Логирование
        Log.info("Server started")
        Log.error("Something failed", exc_info=True)

        # Именованный логгер с контекстом
        log = Log.get("UserService", user_id=42)
        log.info("User created")

        # Декоратор
        @Log.trace(level="INFO", log_args=True)
        async def create_user(...): ...

        # Контекстный менеджер запроса
        async with Log.request("POST", "/users") as log:
            log.info("processing")

        # Отлов исключения с логом
        with Log.catch("db query failed"):
            result = await session.execute(...)
    """

    # ── Настройка ─────────────────────────────────────────────────────────────

    @staticmethod
    def setup(debug: bool = False, env: str = "development") -> None:
        _configurator.configure(debug=debug, env=env)

    # ── Базовые уровни ────────────────────────────────────────────────────────

    @staticmethod
    def debug(msg: str, **kw: Any) -> None:
        logger.opt(depth=1).debug(msg, **kw)

    @staticmethod
    def info(msg: str, **kw: Any) -> None:
        logger.opt(depth=1).info(msg, **kw)

    @staticmethod
    def warning(msg: str, **kw: Any) -> None:
        logger.opt(depth=1).warning(msg, **kw)

    @staticmethod
    def error(msg: str, **kw: Any) -> None:
        logger.opt(depth=1).error(msg, **kw)

    @staticmethod
    def critical(msg: str, **kw: Any) -> None:
        logger.opt(depth=1).critical(msg, **kw)

    @staticmethod
    def exception(msg: str, **kw: Any) -> None:
        """Логирует ERROR + полный traceback текущего исключения."""
        logger.opt(depth=1, exception=True).error(msg, **kw)

    # ── Именованный логгер с контекстом ──────────────────────────────────────

    @staticmethod
    def get(name: str, **context: Any):
        """Возвращает логгер привязанный к имени и контексту."""
        return logger.bind(name=name, **context)

    # ── Декоратор трассировки ─────────────────────────────────────────────────

    @staticmethod
    def trace(
        level: str = "DEBUG",
        log_args: bool = False,
        log_result: bool = False,
        catch: bool = True,
    ) -> Callable:
        """
        Декоратор: логирует вход/выход/время/ошибки функции.

        @Log.trace(level="INFO", log_args=True)
        async def my_func(...): ...
        """
        return log_call(level=level, log_args=log_args, log_result=log_result, catch=catch)

    # ── Контекстный менеджер запроса ──────────────────────────────────────────

    @staticmethod
    def request(method: str, path: str, request_id: str = "", **extra: Any) -> RequestLogger:
        """
        async with Log.request("GET", "/users") as log:
            log.info("handling")
        """
        return RequestLogger(method=method, path=path, request_id=request_id, **extra)

    # ── Отлов исключений ──────────────────────────────────────────────────────

    @staticmethod
    def catch(message: str = ""):
        """
        Контекстный менеджер — логирует исключение и пробрасывает дальше.

        with Log.catch("db query failed"):
            result = await session.execute(...)
        """
        return logger.catch(message=message, reraise=True, onerror=lambda e: None)


# ── Публичные функции для обратной совместимости ──────────────────────────────


def configure_logging(debug: bool = False, env: str = "development") -> None:
    Log.setup(debug=debug, env=env)


def get_logger(name: str, **context: Any):
    return Log.get(name, **context)
