from dataclasses import dataclass, field
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


@dataclass
class _BotGroup:
    name: str
    middleware: list = field(default_factory=list)


class BotRouter:
    """
    Laravel-style fluent router для Aiogram.

    Использование:
        router = BotRouter()

        router.command("start", StartHandler().start)
        router.command("help",  HelpHandler().help)

        with router.group("profile"):
            router.callback(F.data == "profile",  ProfileHandler().show)
            router.callback_data(ProfileCallback, ProfileHandler().handle)
            router.state(ProfileStates.name,       ProfileHandler().get_name)

        dp.include_router(router.build())

    Паттерны:
    - Builder    — fluent регистрация
    - Composite  — группы объединяют роутеры
    - Facade     — скрывает сложность Aiogram Router
    """

    def __init__(self, name: str = "root") -> None:
        self._router = Router(name=name)
        self._children: list[Router] = []
        self._group_stack: list[_BotGroup] = []

    # ── Текущий роутер (учитывает группу) ────────────────────────────────────

    def _current(self) -> Router:
        return self._children[-1] if self._children else self._router

    # ── Group ─────────────────────────────────────────────────────────────────

    def group(self, name: str, middleware: list | None = None):
        """
        Создаёт дочерний Router для группы хэндлеров.

        with router.group("admin"):
            router.command("ban", AdminHandler().ban)
        """
        from contextlib import contextmanager

        @contextmanager
        def _ctx():
            child = Router(name=name)
            for mw in (middleware or []):
                child.message.middleware(mw)
                child.callback_query.middleware(mw)
            self._children.append(child)
            try:
                yield self
            finally:
                finished = self._children.pop()
                self._router.include_router(finished)

        return _ctx()

    # ── Commands ──────────────────────────────────────────────────────────────

    def command(self, cmd: str | list[str], handler, filters: Any = None) -> "BotRouter":
        """
        router.command("start", StartHandler().start)
        router.command(["help", "h"], HelpHandler().help)
        """
        cmds = [cmd] if isinstance(cmd, str) else cmd
        f = Command(*cmds)
        if filters:
            f = f & filters
        self._current().message(f)(handler)
        return self

    # ── Messages ──────────────────────────────────────────────────────────────

    def message(self, filter: Any, handler) -> "BotRouter":
        """
        router.message(F.text, EchoHandler().echo)
        router.message(F.photo, PhotoHandler().handle)
        """
        self._current().message(filter)(handler)
        return self

    def text(self, pattern: str, handler) -> "BotRouter":
        """
        Сообщение с конкретным текстом (кнопки Reply keyboard).

        router.text("📋 Мои задачи", TaskHandler().list)
        """
        self._current().message(F.text == pattern)(handler)
        return self

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def callback(self, filter: Any, handler) -> "BotRouter":
        """
        router.callback(F.data == "profile", ProfileHandler().show)
        router.callback(F.data.startswith("item_"), ItemHandler().handle)
        """
        self._current().callback_query(filter)(handler)
        return self

    def callback_data(self, callback_class: type, handler, **filters) -> "BotRouter":
        """
        Регистрирует CallbackData класс.

        class ProfileCallback(CallbackData, prefix="profile"):
            user_id: int
            action: str

        router.callback_data(ProfileCallback, ProfileHandler().handle)
        router.callback_data(ProfileCallback, handler, action="delete")
        """
        self._current().callback_query(callback_class.filter(**filters) if filters else callback_class.filter())(handler)
        return self

    # ── FSM States ────────────────────────────────────────────────────────────

    def state(self, state: State, handler, message_filter: Any = None) -> "BotRouter":
        """
        router.state(RegisterStates.name, RegHandler().get_name)
        router.state(RegisterStates.email, RegHandler().get_email, F.text)
        """
        f = StateFilter(state)
        if message_filter:
            f = f & message_filter
        self._current().message(f)(handler)
        return self

    def any_state(self, handler, message_filter: Any = None) -> "BotRouter":
        """Хэндлер для любого состояния FSM."""
        f = StateFilter("*")
        if message_filter:
            f = f & message_filter
        self._current().message(f)(handler)
        return self

    # ── Inline Query ──────────────────────────────────────────────────────────

    def inline(self, filter: Any, handler) -> "BotRouter":
        """router.inline(F.query == "", InlineHandler().empty_query)"""
        self._current().inline_query(filter)(handler)
        return self

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> Router:
        """Возвращает корневой Aiogram Router для включения в Dispatcher."""
        return self._router
