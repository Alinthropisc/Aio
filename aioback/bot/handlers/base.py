from abc import ABC, abstractmethod
from typing import Any

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from loguru import logger


# ── Builder паттерн для Inline клавиатур ──────────────────────────────────────

class InlineKeyboard:
    """
    Fluent builder для InlineKeyboardMarkup.

    kb = (
        InlineKeyboard()
        .button("Профиль", callback_data="profile")
        .button("Настройки", callback_data="settings")
        .row()
        .button("Выход", callback_data="logout")
        .build()
    )
    """

    def __init__(self) -> None:
        self._builder = InlineKeyboardBuilder()

    def button(self, text: str, callback_data: str = "", url: str = "") -> "InlineKeyboard":
        if url:
            self._builder.button(text=text, url=url)
        else:
            self._builder.button(text=text, callback_data=callback_data)
        return self

    def row(self, *texts_and_callbacks: tuple[str, str]) -> "InlineKeyboard":
        """Принудительный перенос на новую строку."""
        self._builder.adjust(1)
        if texts_and_callbacks:
            for text, cb in texts_and_callbacks:
                self._builder.button(text=text, callback_data=cb)
        return self

    def adjust(self, *widths: int) -> "InlineKeyboard":
        self._builder.adjust(*widths)
        return self

    def build(self) -> InlineKeyboardMarkup:
        return self._builder.as_markup()


class ReplyKeyboard:
    """
    Fluent builder для ReplyKeyboardMarkup.

    kb = (
        ReplyKeyboard()
        .button("📋 Мои задачи")
        .button("⚙️ Настройки")
        .row()
        .button("🚪 Выход")
        .resize()
        .build()
    )
    """

    def __init__(self) -> None:
        self._builder = ReplyKeyboardBuilder()
        self._resize = True
        self._one_time = False
        self._placeholder: str | None = None

    def button(self, text: str, request_contact: bool = False, request_location: bool = False) -> "ReplyKeyboard":
        self._builder.button(
            text=text,
            request_contact=request_contact,
            request_location=request_location,
        )
        return self

    def row(self) -> "ReplyKeyboard":
        self._builder.adjust(1)
        return self

    def adjust(self, *widths: int) -> "ReplyKeyboard":
        self._builder.adjust(*widths)
        return self

    def resize(self, value: bool = True) -> "ReplyKeyboard":
        self._resize = value
        return self

    def one_time(self, value: bool = True) -> "ReplyKeyboard":
        self._one_time = value
        return self

    def placeholder(self, text: str) -> "ReplyKeyboard":
        self._placeholder = text
        return self

    def build(self) -> ReplyKeyboardMarkup:
        return self._builder.as_markup(
            resize_keyboard=self._resize,
            one_time_keyboard=self._one_time,
            input_field_placeholder=self._placeholder,
        )

    @staticmethod
    def remove() -> ReplyKeyboardRemove:
        return ReplyKeyboardRemove()


# ── Template Method паттерн — базовый хэндлер ────────────────────────────────

class BaseBotHandler(ABC):
    """
    Базовый хэндлер Aiogram — аналог контроллера в веб мире.

    Паттерны:
    - Template Method: _register() переопределяется в каждом хэндлере
    - Builder: InlineKeyboard / ReplyKeyboard для клавиатур
    - Strategy: FSM стратегия для диалогов

    Использование:
        class UserHandler(BaseBotHandler):
            def __init__(self, service: UserService) -> None:
                super().__init__(prefix="user")
                self._service = service
                self._register()

            def _register(self) -> None:
                self.router.message(Command("profile"))(self.show_profile)
                self.router.callback_query(F.data == "delete_account")(self.delete_account)
    """

    def __init__(self, prefix: str = "") -> None:
        self.router = Router(name=prefix or self.__class__.__name__)
        self._log = logger.bind(handler=self.__class__.__name__)
        self._register()

    @abstractmethod
    def _register(self) -> None:
        """Регистрируй роуты через self.router здесь."""

    # ── Message хелперы ───────────────────────────────────────────────────────

    async def reply(self, message: Message, text: str, **kwargs: Any) -> Message:
        return await message.answer(text, **kwargs)

    async def reply_with_inline(
        self, message: Message, text: str, keyboard: InlineKeyboardMarkup, **kwargs: Any
    ) -> Message:
        return await message.answer(text, reply_markup=keyboard, **kwargs)

    async def reply_with_reply_kb(
        self, message: Message, text: str, keyboard: ReplyKeyboardMarkup, **kwargs: Any
    ) -> Message:
        return await message.answer(text, reply_markup=keyboard, **kwargs)

    async def reply_remove_kb(self, message: Message, text: str, **kwargs: Any) -> Message:
        return await message.answer(text, reply_markup=ReplyKeyboard.remove(), **kwargs)

    async def safe_reply(self, message: Message, text: str, **kwargs: Any) -> bool:
        """Отправляет ответ не крашась при ошибке Telegram API."""
        try:
            await message.answer(text, **kwargs)
            return True
        except Exception as exc:
            self._log.error(f"Telegram API error for user {message.from_user.id}: {exc}")
            return False

    async def reply_error(
        self, message: Message, text: str = "Произошла ошибка. Попробуй позже."
    ) -> None:
        self._log.warning(f"Error reply → user {message.from_user.id}")
        await message.answer(text)

    # ── CallbackQuery хелперы ─────────────────────────────────────────────────

    async def answer_callback(
        self,
        callback: CallbackQuery,
        text: str = "",
        show_alert: bool = False,
    ) -> None:
        """Подтверждает нажатие кнопки (убирает часики у пользователя)."""
        await callback.answer(text=text, show_alert=show_alert)

    async def edit_callback_message(
        self,
        callback: CallbackQuery,
        text: str,
        keyboard: InlineKeyboardMarkup | None = None,
        **kwargs: Any,
    ) -> None:
        """Редактирует сообщение под кнопкой."""
        await callback.message.edit_text(text, reply_markup=keyboard, **kwargs)
        await callback.answer()

    async def safe_answer_callback(
        self, callback: CallbackQuery, text: str = "", show_alert: bool = False
    ) -> bool:
        try:
            await callback.answer(text=text, show_alert=show_alert)
            return True
        except Exception as exc:
            self._log.error(f"Callback answer error: {exc}")
            return False

    # ── Keyboard фабрики (паттерн Factory Method) ─────────────────────────────

    def inline_kb(self) -> InlineKeyboard:
        return InlineKeyboard()

    def reply_kb(self) -> ReplyKeyboard:
        return ReplyKeyboard()

    # ── FSM хелперы (паттерн State) ───────────────────────────────────────────

    async def set_state(self, fsm: FSMContext, state: State) -> None:
        await fsm.set_state(state)

    async def get_state(self, fsm: FSMContext) -> str | None:
        return await fsm.get_state()

    async def clear_state(self, fsm: FSMContext) -> None:
        await fsm.clear()

    async def update_data(self, fsm: FSMContext, **kwargs: Any) -> None:
        await fsm.update_data(**kwargs)

    async def get_data(self, fsm: FSMContext) -> dict[str, Any]:
        return await fsm.get_data()

    async def get_and_clear(self, fsm: FSMContext) -> dict[str, Any]:
        """Получает данные FSM и сбрасывает состояние."""
        data = await fsm.get_data()
        await fsm.clear()
        return data

    async def reply_and_next_state(
        self,
        message: Message,
        fsm: FSMContext,
        text: str,
        next_state: State,
        keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
    ) -> None:
        """Отвечает пользователю и переводит FSM в следующее состояние."""
        await message.answer(text, reply_markup=keyboard)
        await fsm.set_state(next_state)
