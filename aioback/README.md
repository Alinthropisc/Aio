# aioback

Async Python backend starter — production-ready архитектура из коробки.

## Стек

| Слой | Технология |
|---|---|
| Сервер | [Granian](https://github.com/emmett-framework/granian) (RSGI) |
| Фреймворк | [Litestar](https://litestar.dev) |
| DI | [Dishka](https://dishka.readthedocs.io) |
| Валидация | [Pydantic v2](https://docs.pydantic.dev) + Pydantic Settings |
| ORM | [SQLAlchemy 2](https://docs.sqlalchemy.org) async |
| Миграции | [Alembic](https://alembic.sqlalchemy.org) |
| БД | PostgreSQL / MySQL |
| Кэш | Redis |
| Бот | [Aiogram 3](https://docs.aiogram.dev) |
| Логи | [Loguru](https://loguru.readthedocs.io) |
| CLI | [Typer](https://typer.tiangolo.com) |

## Структура

```
aioback/
├── app/
│   └── controllers/        # HTTP контроллеры (Litestar)
├── bot/
│   ├── handlers/           # Telegram хэндлеры (Aiogram)
│   └── callbacks/          # CallbackData классы
├── config/                 # Pydantic Settings (app, db, redis, bot)
├── core/
│   ├── auth/               # Gate + Policy (авторизация)
│   ├── cache/              # Redis клиент
│   ├── config/             # BaseAppSettings + кастомные типы
│   ├── db/                 # SQLAlchemy engine, session, base models
│   ├── di/                 # Dishka провайдеры
│   ├── events/             # EventBus (Mediator) + ModelObserver
│   ├── logging/            # Loguru Facade (Log)
│   ├── queue/              # BaseJob + Queue + Worker
│   └── routes/             # ApiRouter + BotRouter (Laravel-style)
├── database/
│   ├── migrations/         # Alembic versions
│   ├── seeders/            # BaseSeeder
│   └── factories/          # BaseFactory + Faker
├── events/                 # Конкретные события приложения
├── i18n/
│   └── locales/            # en.json, ru.json
├── jobs/                   # Конкретные Job классы
├── listeners/              # BaseListener + ListenerRegistry
├── middleware/
│   ├── http/               # LoggingMiddleware, RequestIdMiddleware
│   └── bot/                # ThrottleMiddleware, BotAuthMiddleware
├── observers/              # Конкретные Observer классы
├── repositories/           # BaseRepository (Generic CRUD)
├── routes/
│   ├── api.py              # Регистрация HTTP маршрутов
│   └── bot.py              # Регистрация Bot маршрутов
├── schemas/                # Pydantic DTO (BaseSchema, SuccessResponse, PaginatedResponse)
├── scripts/
│   └── cli.py              # Typer CLI (aioback команды)
├── services/               # BaseService
├── workers/
│   └── main.py             # Запуск воркера очереди
├── main.py                 # Точка входа Litestar
├── .env.example
└── alembic.ini
```

## Быстрый старт

```bash
# 1. Клонировать и установить зависимости
git clone <repo>
cd aioback
uv sync

# 2. Настроить окружение
cp .env.example .env

# 3. Применить миграции
aioback db migrate

# 4. Запустить сервер
granian --interface rsgi main:app --reload

# 5. Запустить воркер (отдельный терминал)
aioback worker --queues default,emails
```

## CLI

```bash
aioback info

# База данных
aioback db migrate
aioback db rollback --steps 1
aioback db revision -m "add users"
aioback db status
aioback db seed

# Воркер
aioback worker --queues default,emails --concurrency 5

# Генераторы
aioback make model User
aioback make service User
aioback make repository User
aioback make controller User
aioback make job SendEmail
aioback make observer User
aioback make listener SendWelcome
```

## Архитектура слоёв

```
Controller / Handler
       ↓
    Service          ← бизнес логика
       ↓
  Repository         ← работа с БД
       ↓
     Model           ← SQLAlchemy
```

Сервис не знает про HTTP или Telegram — одна бизнес логика для обоих интерфейсов.

## Примеры

### Модель

```python
from core.db import BaseSoftModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(BaseSoftModel):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

### Репозиторий

```python
from repositories import BaseRepository

class UserRepository(BaseRepository[User]):
    model = User
```

### Сервис

```python
from services import BaseService

class UserService(BaseService[User, UserRepository]):
    async def before_create(self, data: dict) -> dict:
        data["password"] = self._hasher.hash(data["password"])
        return data
```

### HTTP контроллер (Litestar)

```python
from dishka.integrations.litestar import FromDishka, inject
from litestar import get
from app.controllers import BaseWebController

class UserController(BaseWebController):
    path = "/users"

    @get()
    @inject
    async def index(self, service: FromDishka[UserService]) -> list:
        page = await service.paginate(limit=20, offset=0)
        return self.paginated(page)
```

### Bot хэндлер (Aiogram)

```python
from bot.handlers import BaseBotHandler
from aiogram.filters import Command
from aiogram.types import Message

class UserHandler(BaseBotHandler):
    def __init__(self, service: UserService) -> None:
        super().__init__(prefix="user")
        self._service = service

    def _register(self) -> None:
        self.router.message(Command("profile"))(self.profile)

    async def profile(self, message: Message) -> None:
        user = await self._service.get_by(telegram_id=message.from_user.id)
        kb = self.inline_kb().button("Изменить", "edit_profile").build()
        await self.reply_with_inline(message, f"Привет, {user.name}!", kb)
```

### Events & Listeners

```python
from core.events.bus import event_bus

@event_bus.on(UserCreatedEvent)
async def send_welcome(event: UserCreatedEvent) -> None:
    await mailer.send(event.instance.email)
```

### Jobs & Queue

```python
@dataclass
class SendEmailJob(BaseJob):
    queue: str = "emails"
    max_retries: int = 3
    to: str = ""

    async def handle(self) -> None:
        await mailer.send(self.to)

await queue.push(SendEmailJob(to="user@example.com"))
await queue.push(SendEmailJob(to="user@example.com"), delay=60)
```

### Gate & Policy

```python
from core.auth import gate

gate.define("edit-post", lambda user, post: post.author_id == user.id)
gate.before(lambda user: user.role == "superadmin")

await gate.authorize("edit-post", user, post)
await gate.any(["admin", "moderator"], user)
```

### Роутинг (Laravel-style)

```python
# HTTP
with router.group("/api/v1", tags=["v1"]):
    router.resource("/users", UserController)
    with router.group("/admin", middleware=[AuthMiddleware]):
        router.get("/stats", StatsController.stats)

# Bot
router.command("start", StartHandler().handle)
router.text("👤 Профиль", ProfileHandler().show)
with router.group("profile"):
    router.callback_data(ProfileCallback, ProfileHandler().handle)
    router.state(ProfileStates.editing, ProfileHandler().edit)
```

### i18n

```python
from i18n import t, set_locale

set_locale("ru")
t("errors.not_found", entity="User")  # "User не найден"
t("auth.login.success")               # "Вход выполнен успешно"
```

## Паттерны проектирования

| Паттерн | Где используется |
|---|---|
| **Repository** | `BaseRepository` — изоляция работы с БД |
| **Service Layer** | `BaseService` — бизнес логика |
| **Dependency Injection** | Dishka — `Provider`, `Scope`, `@inject` |
| **Observer** | `ModelObserver` + `ObservableMixin` |
| **Mediator** | `EventBus` — шина событий |
| **Command** | `BaseJob` — инкапсуляция задачи |
| **Builder** | `InlineKeyboard`, `ReplyKeyboard`, `BaseFactory` |
| **Facade** | `Log`, `ApiRouter`, `Translator` |
| **Strategy** | `Gate.define()`, `ThrottleMiddleware` |
| **Factory Method** | `build_container()`, `create_engine()` |
| **Singleton** | `get_settings()`, `event_bus`, `gate` |
| **Template Method** | `BaseJob.handle()`, `BaseListener.handle()`, `BaseBotHandler._register()` |
| **Registry** | `PolicyRegistry`, `ListenerRegistry` |
| **Chain of Responsibility** | Middleware Litestar и Aiogram |
| **Composite** | `ApiRouter.group()`, `BotRouter.group()` |

## GitHub Actions

| Workflow | Триггер | Что делает |
|---|---|---|
| `ci.yml` | push / PR | Ruff lint + format check |
| `tests.yml` | push / PR | pytest + PostgreSQL + Redis + Codecov |
| `benchmark.yml` | push main | Granian + wrk нагрузка + артефакт |
| `release.yml` | tag `v*.*.*` | build + GitHub Release |

## Переменные окружения

```env
APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

DB_HOST=localhost
DB_NAME=aioback
DB_USER=postgres
DB_PASSWORD=postgres

SECONDARY_DB_ENABLED=false

REDIS_HOST=localhost
REDIS_PORT=6379

BOT_TOKEN=your_token_here
```

Полный список в `.env.example`.
