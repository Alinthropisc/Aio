# aiofront

![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)
![License](https://img.shields.io/badge/license-MIT-green)

Next.js 15 web frontend for the Aio platform.

## Features

- **App Router & Server Components** — file-based routing with React Server Components for optimal performance
- **Authentication** — next-auth v5 with session management and protected routes
- **Internationalisation** — next-intl for locale-aware routing and message translation
- **Data Fetching** — TanStack Query for server-state caching, background refetching, and optimistic updates
- **Styling** — Tailwind CSS utility-first design system, integrated with `@aio/ui` shared components
- **Unit Tests** — Vitest with React Testing Library

## Tech Stack

| Layer | Library / Tool |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript 5 |
| Auth | next-auth v5 |
| i18n | next-intl |
| Data fetching | TanStack Query + Axios |
| Styling | Tailwind CSS |
| Shared UI | @aio/ui |
| Shared types | @aio/types |
| Testing | Vitest |

## Getting Started

### Prerequisites

- Node.js 20+
- pnpm 9+

### Install & run

```bash
# from monorepo root
pnpm install

# copy environment template
cp aiofront/.env.example aiofront/.env.local

# start dev server
pnpm dev
```

Or from inside `aiofront/`:

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

## Project Structure

```
aiofront/
  src/
    app/          # App Router pages and layouts
    components/   # Feature and shared UI components
    lib/          # Axios client, auth helpers, query hooks
  messages/       # i18n translation files (next-intl)
  tests/          # Vitest unit tests
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `NEXTAUTH_SECRET` | yes | Secret used to sign session tokens |
| `NEXTAUTH_URL` | yes | Canonical URL of the app (e.g. `http://localhost:3000`) |
| `NEXT_PUBLIC_API_URL` | yes | Base URL of the aioback REST API |

Copy `.env.example` to `.env.local` and fill in values before starting the dev server.

## Scripts

| Script | Command | Description |
|---|---|---|
| dev | `pnpm dev` | Start Next.js dev server on port 3000 |
| build | `pnpm build` | Production build |
| test | `pnpm test` | Run Vitest unit tests |
| lint | `pnpm lint` | ESLint check |

## License

MIT
