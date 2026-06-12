# aioback

![Python 3.13](https://img.shields.io/badge/python-3.13-blue?logo=python&logoColor=white)
![Litestar](https://img.shields.io/badge/litestar-2.24-7c3aed?logo=python&logoColor=white)
![License MIT](https://img.shields.io/badge/license-MIT-green)

Production-ready async Python backend — Litestar REST API + Aiogram 3 Telegram bot, clean architecture out of the box.

## Features

- **Litestar 2.24 REST API** — type-safe controllers, OpenAPI docs, response caching
- **Aiogram 3 Telegram bot** — handlers, callbacks, FSM states, inline keyboards
- **Granian RSGI server** — high-performance Rust-based ASGI/RSGI server
- **Alembic migrations** — versioned schema migrations with CLI helpers
- **PostgreSQL + Redis** — async SQLAlchemy 2 ORM, async Redis cache layer
- **Clean architecture** — Controller → Service → Repository → Model layering
- **DI with Dishka** — scoped dependency injection, provider-based container
- **i18n** — JSON-based locale files, `t()` helper, per-request locale switching

## Tech Stack

| Layer | Technology |
|---|---|
| Server | [Granian](https://github.com/emmett-framework/granian) (RSGI) |
| Framework | [Litestar 2.24](https://litestar.dev) |
| Language | Python 3.13 |
| DI | [Dishka](https://dishka.readthedocs.io) |
| Validation | [Pydantic v2](https://docs.pydantic.dev) + Pydantic Settings |
| ORM | [SQLAlchemy 2](https://docs.sqlalchemy.org) async |
| Migrations | [Alembic](https://alembic.sqlalchemy.org) |
| Database | PostgreSQL |
| Cache | Redis |
| Telegram bot | [Aiogram 3](https://docs.aiogram.dev) |
| Logging | [Loguru](https://loguru.readthedocs.io) |
| CLI | [Typer](https://typer.tiangolo.com) |

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Clone the monorepo and enter the backend package
git clone <repo-url>
cd aioback

# Copy environment config
cp .env.example .env
# Edit .env and fill in DB_PASSWORD, BOT_TOKEN, etc.

# Install dependencies
uv sync

# Apply database migrations
alembic upgrade head

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`. OpenAPI docs at `http://localhost:8000/schema`.

## Project Structure

```
aioback/
├── app/
│   └── controllers/        # Litestar HTTP controllers
├── bot/
│   ├── handlers/           # Aiogram message/command handlers
│   └── callbacks/          # CallbackData classes
├── config/                 # Pydantic Settings (app, db, redis, bot)
├── core/
│   ├── auth/               # Gate + PolicyRegistry (authorization)
│   ├── cache/              # Async Redis client wrapper
│   ├── db/                 # SQLAlchemy engine, session, base models
│   ├── di/                 # Dishka providers and container builder
│   ├── events/             # EventBus (Mediator pattern)
│   ├── logging/            # Loguru facade (Log)
│   ├── queue/              # BaseJob + Queue + Worker
│   └── routes/             # ApiRouter + BotRouter (Laravel-style)
├── database/
│   ├── migrations/         # Alembic version files
│   ├── seeders/            # BaseSeeder
│   └── factories/          # BaseFactory + Faker integration
├── events/                 # Application-level event classes
├── i18n/
│   └── locales/            # en.json, ru.json
├── jobs/                   # Concrete Job classes
├── listeners/              # BaseListener + ListenerRegistry
├── middleware/
│   ├── http/               # LoggingMiddleware, RequestIdMiddleware
│   └── bot/                # ThrottleMiddleware, BotAuthMiddleware
├── observers/              # Concrete ModelObserver classes
├── repositories/           # BaseRepository (Generic async CRUD)
├── routes/
│   ├── api.py              # HTTP route registration
│   └── bot.py              # Bot route registration
├── schemas/                # Pydantic DTOs (BaseSchema, PaginatedResponse)
├── scripts/
│   └── cli.py              # Typer CLI entry point
├── services/               # BaseService (business logic layer)
├── workers/
│   └── main.py             # Queue worker entry point
├── tests/                  # pytest test suite
├── main.py                 # Litestar app entry point
├── pyproject.toml
├── alembic.ini
└── .env.example
```

## Development

```bash
# Run the dev server with auto-reload
granian --interface rsgi main:app --reload

# Run the Telegram bot worker (separate terminal)
python workers/main.py

# Run the CLI
python scripts/cli.py --help

# Lint and format
ruff check .
ruff format .

# Type checking
mypy .

# Run tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=term-missing --cov-report=xml
```

### Database migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "add users table"

# Roll back one step
alembic downgrade -1

# Show current migration state
alembic current
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Runtime environment (`development`, `production`) |
| `APP_DEBUG` | `true` | Enable debug mode and verbose logging |
| `APP_HOST` | `0.0.0.0` | Server bind host |
| `APP_PORT` | `8000` | Server bind port |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `aioback` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | _(required)_ | PostgreSQL password |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database index |
| `BOT_TOKEN` | _(required)_ | Telegram Bot API token |
| `BOT_WEBHOOK_URL` | _(optional)_ | Webhook URL for production bot mode |

Full list with defaults is in `.env.example`.

## License

[MIT](../LICENSE)
