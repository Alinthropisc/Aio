# Aio Frontend Design Spec
**Date:** 2026-06-12  
**Status:** Approved

---

## Overview

Aio is an Open Source Full-Stack Starter Template Kit. Frontend consists of two Next.js 15 apps sharing a common UI package.

---

## Monorepo Structure

```
Aio/
├── aioback/                  # Python backend (Litestar + Aiogram)
├── aiofront/                 # Next.js 15 — web site + admin panel
├── aiomini/                  # Next.js 15 — Telegram MiniApp
├── packages/
│   ├── ui/                   # shadcn/ui shared components + design tokens
│   ├── types/                # TypeScript types (mirrors aioback schemas)
│   └── config/               # shared tailwind.config, eslint, tsconfig
└── .github/
    └── workflows/
```

---

## Tech Stack (both apps)

| Layer | Library |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| UI | shadcn/ui + TailwindCSS v4 |
| Data fetching | TanStack Query v5 |
| Client state | Zustand |
| Auth | NextAuth.js v5 (credentials → aioback JWT) |
| i18n | next-intl (RU + EN, structure ready) |
| HTTP | axios |
| Validation | Zod |
| Telegram SDK | @twa-dev/sdk (aiomini only) |

---

## Design Patterns

- **Feature-based folder structure** — `features/auth/`, `features/users/`, not `components/pages/`
- **Repository pattern** — `lib/api/` wraps all axios calls, TanStack Query consumes repos
- **Custom hooks** — business logic in `use*.ts` hooks, not in components
- **Compound components** — complex UI (tables, forms, modals) as compound components in `packages/ui`
- **Design tokens** — all colors, spacing, radii in `packages/ui/tokens`, swap to restyle everything

---

## aiofront — Pages

### Public
- `/` — Landing page
- `/login` — Login
- `/register` — Register
- `/forgot-password` — Password reset

### User (authenticated)
- `/dashboard` — main dashboard
- `/profile` — user profile
- `/settings` — user settings
- `/notifications` — notifications

### Admin (role: admin)
- `/admin` — overview
- `/admin/users` — Users CRUD
- `/admin/settings` — system settings

---

## aiomini — Pages (Telegram MiniApp)

No admin panel. Pure user-facing interface, designed for easy theme customization.

- `/` — Home (user profile/data overview)
- `/settings` — user settings
- `/notifications` — notifications

**Auth:** Auto-login via Telegram `initData` passed to aioback for verification.

---

## i18n

- Locales: `ru`, `en` (default: `ru`)
- Translation files: `messages/ru.json`, `messages/en.json`
- Keys: navigation labels, page titles, common errors, form labels, auth messages

---

## GitHub Actions

### aiofront/.github/workflows/
- `ci.yml` — ESLint + TypeScript check + Next.js build (on push/PR)
- `deploy.yml` — deploy to Vercel or self-hosted

### aiomini/.github/workflows/
- `ci.yml` — same as aiofront
- `deploy.yml` — deploy (Vercel recommended for MiniApp)
