from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import BaseModel

Model = TypeVar("Model", bound=BaseModel)

fake = Faker()


class BaseFactory(ABC, Generic[Model]):
    """
    Базовая фабрика тестовых данных (паттерн Factory + Builder).

    Использование:
        class UserFactory(BaseFactory[User]):
            model = User

            def definition(self) -> dict[str, Any]:
                return {
                    "name": fake.name(),
                    "email": fake.unique.email(),
                    "password": "hashed_password",
                }

        # Создать одного
        user = await UserFactory().create(session)

        # Создать с перегрузкой полей
        admin = await UserFactory().create(session, role="admin")

        # Создать батч
        users = await UserFactory().create_batch(session, count=10)
    """

    model: type[Model]

    def __init__(self) -> None:
        self._overrides: dict[str, Any] = {}

    @abstractmethod
    def definition(self) -> dict[str, Any]:
        """Определи дефолтные поля модели."""

    def make(self, **overrides: Any) -> Model:
        """Создаёт объект модели без сохранения в БД."""
        data = {**self.definition(), **self._overrides, **overrides}
        return self.model(**data)

    async def create(self, session: AsyncSession, **overrides: Any) -> Model:
        """Создаёт и сохраняет один объект в БД."""
        instance = self.make(**overrides)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def create_batch(self, session: AsyncSession, count: int = 5, **overrides: Any) -> list[Model]:
        """Создаёт и сохраняет несколько объектов в БД."""
        instances = [self.make(**overrides) for _ in range(count)]
        session.add_all(instances)
        await session.flush()
        return instances

    def with_fields(self, **overrides: Any) -> "BaseFactory[Model]":
        """Fluent setter — переопределяет поля до вызова create."""
        self._overrides.update(overrides)
        return self
