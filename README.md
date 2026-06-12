# Aio — Full-Stack Monorepo Starter Kit

> Production-ready monorepo with a Python async backend, Next.js web frontend, Telegram Mini App, and Flutter mobile app — all sharing types and a common design system.

[![CI — aioback](https://github.com/aio-dev/aio/actions/workflows/aioback.yml/badge.svg)](https://github.com/aio-dev/aio/actions/workflows/aioback.yml)
[![CI — aiofront](https://github.com/aio-dev/aio/actions/workflows/aiofront.yml/badge.svg)](https://github.com/aio-dev/aio/actions/workflows/aiofront.yml)
[![CI — aiomini](https://github.com/aio-dev/aio/actions/workflows/aiomini.yml/badge.svg)](https://github.com/aio-dev/aio/actions/workflows/aiomini.yml)
[![CI — aiomobile](https://github.com/aio-dev/aio/actions/workflows/aiomobile.yml/badge.svg)](https://github.com/aio-dev/aio/actions/workflows/aiomobile.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What Is Aio?

Aio is an opinionated, production-grade starter kit for teams that ship across **web, Telegram, and mobile** from a single codebase. It eliminates the bootstrap overhead — auth, DI, routing, CI, shared types, and design tokens are all wired up out of the box.

You clone it, rename it, and start building features on day one.

---

## Monorepo Structure

```
aio/
├── aioback/          # Python async REST API + Telegram bot
├── aiofront/         # Next.js 15 web application
├── aiomini/          # Telegram Mini App (React + Vite)
├── aiomobile/        # Flutter mobile app (Android + iOS)
├── packages/
│   ├── config/       # Shared ESLint + TypeScript configs
│   ├── types/        # Shared TypeScript types (API contracts)
│   └── ui/           # Shared React component library
├── docs/             # Architecture docs
├── docker-compose.yml
└── Makefile
```

---

## Apps & Packages

### `aioback` — Python Async Backend

The core API server and Telegram bot worker.

| Layer | Technology |
|---|---|
| Framework | [Litestar](https://litestar.dev) 2.24 |
| Server | [Granian](https://github.com/emmett-framework/granian) (RSGI) |
| Telegram Bot | [Aiogram](https://aiogram.dev) 3 |
| Database | PostgreSQL + [Alembic](https://alembic.sqlalchemy.org) |
| Cache / Queue | Redis |
| DI | [Dishka](https://github.com/reagento/dishka) |
| Runtime | Python 3.13 |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| Linting | Ruff + Mypy |

→ [aioback/README.md](aioback/README.md)

---

### `aiofront` — Web Frontend

Server-rendered web app with authentication and i18n.

| Layer | Technology |
|---|---|
| Framework | [Next.js](https://nextjs.org) 15 (App Router) |
| Language | TypeScript 5 |
| Auth | [NextAuth.js](https://next-auth.js.org) v5 |
| Data fetching | [TanStack Query](https://tanstack.com/query) v5 |
| i18n | [next-intl](https://next-intl-docs.vercel.app) |
| Styling | Tailwind CSS v4 |
| Testing | Vitest + Testing Library |

→ [aiofront/README.md](aiofront/README.md)

---

### `aiomini` — Telegram Mini App

Lightweight SPA running inside Telegram.

| Layer | Technology |
|---|---|
| Framework | React 19 + [Vite](https://vitejs.dev) |
| Telegram SDK | [@twa-dev/sdk](https://github.com/twa-dev/SDK) |
| State | [Zustand](https://zustand-demo.pmnd.rs) |
| Data fetching | TanStack Query |
| Validation | [Zod](https://zod.dev) |
| Styling | Tailwind CSS (CVA + clsx) |
| Testing | Vitest |

→ [aiomini/README.md](aiomini/README.md)

---

### `aiomobile` — Flutter Mobile App

Native Android and iOS app with clean architecture.

| Layer | Technology |
|---|---|
| Framework | [Flutter](https://flutter.dev) 3.44 / Dart 3.12 |
| State | [flutter_bloc](https://bloclibrary.dev) 9 + hydrated_bloc |
| DI | [get_it](https://pub.dev/packages/get_it) + [injectable](https://pub.dev/packages/injectable) |
| Navigation | [go_router](https://pub.dev/packages/go_router) 15 |
| HTTP | [Dio](https://pub.dev/packages/dio) 5 (with auto token refresh) |
| Storage | flutter_secure_storage + shared_preferences |
| Codegen | freezed + injectable_generator |
| Testing | flutter_test + bloc_test + mocktail |

→ [aiomobile/README.md](aiomobile/README.md)

---

### `packages/types`

Shared TypeScript types that mirror the `aioback` API response schemas. Used by both `aiofront` and `aiomini` — change the API contract once, fix compile errors everywhere.

### `packages/ui`

Shared React component library (buttons, inputs, cards) consumed by `aiofront` and `aiomini`. Built on Tailwind CSS and Radix UI primitives.

### `packages/config`

Shared `tsconfig.json` base and ESLint flat config presets for all JS/TS packages.

---

## Getting Started

### Prerequisites

| Tool | Version |
|---|---|
| Node.js | 20+ |
| npm | 10+ |
| Python | 3.13+ |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest |
| Flutter | 3.44+ |
| Docker + Compose | latest |

### 1. Clone

```bash
git clone https://github.com/your-org/aio.git
cd aio
```

### 2. Start infrastructure

```bash
docker-compose up -d        # PostgreSQL + Redis
```

### 3. Backend

```bash
cd aioback
cp .env.example .env        # fill in your values
uv sync
alembic upgrade head
python main.py
```

### 4. Web frontend

```bash
cd aiofront
cp .env.example .env.local
npm install
npm run dev
```

### 5. Telegram Mini App

```bash
cd aiomini
cp .env.example .env
npm install
npm run dev
```

### 6. Mobile

```bash
cd aiomobile
flutter pub get
dart run build_runner build --delete-conflicting-outputs
flutter run
```

### Or use Make

```bash
make install     # install all deps
make dev         # start backend + frontend in parallel
make test        # run all test suites
make lint        # lint all packages
```

---

## Architecture

```
                    ┌─────────────────────────────────┐
                    │          aioback (API)           │
                    │  Litestar REST  │  Aiogram Bot   │
                    └────────┬────────┴───────┬────────┘
                             │                │
              ┌──────────────┼────────────────┤
              │              │                │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
     │   aiofront    │ │  aiomini   │ │  aiomobile  │
     │  Next.js 15   │ │ Telegram   │ │   Flutter   │
     │  Web App      │ │ Mini App   │ │ Android/iOS │
     └───────────────┘ └────────────┘ └─────────────┘
              │              │
     ┌────────▼──────────────▼──────┐
     │       packages/types         │
     │   Shared TypeScript types    │
     └──────────────────────────────┘
```

All frontend apps talk to `aioback` over a versioned REST API (`/api/v1`). Shared types in `packages/types` keep request/response shapes in sync across TS consumers. Flutter uses its own Dart models that mirror the same API contracts.

---

## Development

### Run all JS tests

```bash
npm test
```

### Run backend tests

```bash
cd aioback && pytest --cov
```

### Run Flutter tests

```bash
cd aiomobile && flutter test
```

### Lint everything

```bash
npm run lint          # all JS/TS packages
cd aioback && ruff check .
cd aiomobile && flutter analyze
```

### Type check

```bash
npm run typecheck
```

---

## Environment Variables

Copy `.env.example` to `.env` in the repo root (used by Docker Compose) and in each app subdirectory.

| Variable | Used by | Description |
|---|---|---|
| `DATABASE_URL` | aioback | PostgreSQL connection string |
| `REDIS_URL` | aioback | Redis connection string |
| `SECRET_KEY` | aioback | App secret for JWT signing |
| `BOT_TOKEN` | aioback | Telegram bot token |
| `NEXTAUTH_SECRET` | aiofront | NextAuth signing secret |
| `NEXTAUTH_URL` | aiofront | Public URL of the web app |
| `NEXT_PUBLIC_API_URL` | aiofront | Backend API base URL |
| `VITE_API_URL` | aiomini | Backend API base URL |
| `VITE_BOT_USERNAME` | aiomini | Telegram bot username |
| `API_BASE_URL` | aiomobile | Backend API base URL (dart-define) |

---

## CI / CD

Each app has its own GitHub Actions workflow that triggers only on changes to its own directory:

| Workflow | Triggers on | Jobs |
|---|---|---|
| `aioback.yml` | `aioback/**` | ruff, mypy, pytest, docker build |
| `aiofront.yml` | `aiofront/**`, `packages/**` | lint, test, build |
| `aiomini.yml` | `aiomini/**`, `packages/**` | lint, test, build |
| `aiomobile.yml` | `aiomobile/**` | analyze, flutter test, apk build |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming, commit conventions, and PR process.

---

## License

MIT — see [LICENSE](LICENSE) for details.
