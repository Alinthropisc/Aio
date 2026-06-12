# aiomini

![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Mini%20App-26A5E4?logo=telegram&logoColor=white)

Telegram Mini App built with React + Vite. Part of the [Aio monorepo](../README.md).

---

## Features

- **Telegram Web App SDK** — full `@twa-dev/sdk` integration: theme params, main button, back button, haptic feedback, launch params
- **Zustand** state management with devtools support
- **TanStack Query** for server state, caching, and background refetching
- **Zod** schema validation for API responses and environment variables
- **Vite HMR** for instant feedback during development
- **Vitest** unit and integration tests with jsdom

---

## Tech Stack

| Layer | Library |
|---|---|
| UI | React 18 |
| Language | TypeScript 5 |
| Bundler | Vite 5 |
| Styling | Tailwind CSS + clsx + tailwind-merge + CVA |
| Client state | Zustand |
| Server state | TanStack Query (React Query) |
| Validation | Zod |
| Telegram SDK | @twa-dev/sdk |
| Testing | Vitest + @testing-library/react |

---

## Getting Started

**Requirements:** Node 20+, pnpm 9+

```bash
# 1. Install dependencies from the repo root
pnpm install

# 2. Copy the environment template
cp .env.example .env

# 3. Start the dev server
pnpm dev
```

The app will be available at `http://localhost:5173`.

---

## Telegram Setup

### Register with BotFather

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts to create a bot.
3. Send `/mybots` → select your bot → **Bot Settings** → **Menu Button** → set the URL to your Mini App URL.

### Set a Webhook (for backend notifications)

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/api/telegram/webhook"}'
```

### Local testing with ngrok

```bash
# Expose your local dev server
ngrok http 5173

# Use the generated https URL in BotFather and as VITE_API_URL
```

---

## Project Structure

```
aiomini/
src/
  app/           # App bootstrap: providers, router, global styles
  entities/      # Domain models (user, order, …) — types + stores + queries
  features/      # Self-contained feature slices
  shared/        # Reusable UI components, hooks, utils, api client
tests/           # Vitest test files
index.html
vite.config.ts
vitest.config.ts
```

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Base URL of the Aio backend | `https://api.aio.example.com` |
| `VITE_BOT_USERNAME` | Telegram bot username (without @) | `AioBot` |

Copy `.env.example` to `.env` and fill in values before running locally.

---

## Scripts

| Command | Description |
|---|---|
| `pnpm dev` | Start Vite dev server with HMR |
| `pnpm build` | Production build to `dist/` |
| `pnpm preview` | Serve the production build locally |
| `pnpm test` | Run Vitest in watch mode |
| `pnpm test run` | Run Vitest once (CI mode) |
| `pnpm lint` | Run ESLint |

---

## License

MIT
