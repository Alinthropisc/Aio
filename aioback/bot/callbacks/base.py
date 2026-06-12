from aiogram.filters.callback_data import CallbackData


class ActionCallback(CallbackData, prefix="action"):
    """
    Универсальный callback для простых действий.

    Пример:
        kb.button("Удалить", callback_data=ActionCallback(entity="user", id=str(user.id), action="delete").pack())
    """

    entity: str
    id: str
    action: str


class ConfirmCallback(CallbackData, prefix="confirm"):
    """
    Callback для подтверждения действия (да/нет).

    Пример:
        kb.button("✅ Да", callback_data=ConfirmCallback(action="delete_user", id=str(user.id), confirmed=True).pack())
        kb.button("❌ Нет", callback_data=ConfirmCallback(action="delete_user", id=str(user.id), confirmed=False).pack())
    """

    action: str
    id: str
    confirmed: bool
