from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import Log


class BaseSeeder(ABC):
    """
    Базовый сидер — наполняет БД начальными данными.

    Использование:
        class UserSeeder(BaseSeeder):
            name = "users"

            async def run(self, session: AsyncSession) -> None:
                await session.execute(insert(User).values([...]))
                await session.commit()
                self.done(3)
    """

    name: str = ""

    def __init__(self) -> None:
        self._log = Log.get("Seeder", seeder=self.name or self.__class__.__name__)

    @abstractmethod
    async def run(self, session: AsyncSession) -> None:
        """Реализуй логику наполнения данными."""

    def done(self, count: int) -> None:
        self._log.info(f"Seeded {count} record(s)")
