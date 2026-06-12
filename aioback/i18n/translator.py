import json
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from core.logging import Log

_locale_var: ContextVar[str] = ContextVar("locale", default="en")
_LOCALES_DIR = Path("i18n/locales")


class Translator:
    """
    Система переводов — паттерн Facade + Strategy.
    Вложенные ключи: t("auth.login.success")
    Плейсхолдеры:    t("errors.not_found", entity="User")
    """

    def __init__(self, locales_dir: Path = _LOCALES_DIR, default_locale: str = "en") -> None:
        self._dir = locales_dir
        self._default = default_locale
        self._cache: dict[str, dict] = {}
        self._log = Log.get("i18n")
        self._load_all()

    def _load_all(self) -> None:
        if not self._dir.exists():
            self._dir.mkdir(parents=True, exist_ok=True)
            return
        for path in self._dir.glob("*.json"):
            locale = path.stem
            try:
                with open(path, encoding="utf-8") as f:
                    self._cache[locale] = json.load(f)
                self._log.debug(f"Loaded locale: {locale}")
            except Exception as exc:
                self._log.error(f"Failed to load locale {locale}: {exc}")

    def _resolve(self, data: dict, key: str) -> str | None:
        parts = key.split(".")
        current = data
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current if isinstance(current, str) else None

    def translate(self, key: str, locale: str | None = None, **kwargs: Any) -> str:
        loc = locale or _locale_var.get()
        data = self._cache.get(loc, self._cache.get(self._default, {}))
        text = self._resolve(data, key)

        if text is None and loc != self._default:
            text = self._resolve(self._cache.get(self._default, {}), key)

        if text is None:
            self._log.warning(f"Missing translation: [{loc}] {key}")
            return key

        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

    def reload(self) -> None:
        self._cache.clear()
        self._load_all()

    def available_locales(self) -> list[str]:
        return list(self._cache.keys())


_translator = Translator()


def t(key: str, locale: str | None = None, **kwargs: Any) -> str:
    return _translator.translate(key, locale=locale, **kwargs)


def set_locale(locale: str) -> None:
    _locale_var.set(locale)


def get_locale() -> str:
    return _locale_var.get()
