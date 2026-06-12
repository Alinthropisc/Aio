# Packages Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create shared `packages/` monorepo foundation — config, TypeScript types, and shadcn/ui component library used by both aiofront and aiomini.

**Architecture:** Three packages under `packages/`: `config` (shared tsconfig/eslint/tailwind), `types` (TypeScript interfaces mirroring aioback schemas), `ui` (shadcn/ui components + design tokens). Each package is a standalone npm package imported by the apps.

**Tech Stack:** TypeScript 5, TailwindCSS v4, shadcn/ui, Radix UI, Vitest, React Testing Library

---

## File Map

```
packages/
├── config/
│   ├── package.json
│   ├── tsconfig.base.json
│   ├── tsconfig.nextjs.json
│   └── eslint.config.js
├── types/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts
│       ├── user.ts
│       ├── auth.ts
│       └── common.ts
└── ui/
    ├── package.json
    ├── tsconfig.json
    ├── vitest.config.ts
    ├── src/
    │   ├── index.ts
    │   ├── lib/utils.ts
    │   ├── tokens/index.ts
    │   └── components/
    │       ├── button.tsx
    │       ├── input.tsx
    │       ├── card.tsx
    │       └── badge.tsx
    └── tests/
        ├── setup.ts
        └── button.test.tsx
```

---

### Task 1: Root monorepo setup

**Files:**
- Create: `package.json` (root)
- Create: `.npmrc`

- [ ] **Step 1: Create root package.json**

```json
{
  "name": "aio",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "packages/*",
    "aiofront",
    "aiomini"
  ],
  "scripts": {
    "build": "npm run build --workspaces --if-present",
    "lint": "npm run lint --workspaces --if-present",
    "typecheck": "npm run typecheck --workspaces --if-present",
    "test": "npm run test --workspaces --if-present"
  },
  "devDependencies": {
    "typescript": "^5.5.0"
  }
}
```

- [ ] **Step 2: Create .npmrc**

```ini
shamefully-hoist=true
```

- [ ] **Step 3: Install root deps**

```bash
cd /home/sayavdera/Desktop/projects/Web/Aio
npm install
```

Expected: `node_modules/` created at root.

- [ ] **Step 4: Init git and commit**

```bash
git init
git add package.json .npmrc
git commit -m "chore: init monorepo workspace"
```

---

### Task 2: packages/config

**Files:**
- Create: `packages/config/package.json`
- Create: `packages/config/tsconfig.base.json`
- Create: `packages/config/tsconfig.nextjs.json`
- Create: `packages/config/eslint.config.js`

- [ ] **Step 1: Create packages/config/package.json**

```json
{
  "name": "@aio/config",
  "version": "0.0.1",
  "private": true,
  "exports": {
    "./tsconfig": "./tsconfig.base.json",
    "./tsconfig/nextjs": "./tsconfig.nextjs.json",
    "./eslint": "./eslint.config.js"
  }
}
```

- [ ] **Step 2: Create tsconfig.base.json**

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true,
    "moduleDetection": "force",
    "allowJs": true,
    "resolveJsonModule": true,
    "moduleResolution": "bundler",
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "skipLibCheck": true
  }
}
```

- [ ] **Step 3: Create tsconfig.nextjs.json**

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }]
  }
}
```

- [ ] **Step 4: Create eslint.config.js**

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/consistent-type-imports": "error",
    },
  }
);
```

- [ ] **Step 5: Commit**

```bash
git add packages/config/
git commit -m "chore: add @aio/config shared tsconfig and eslint"
```

---

### Task 3: packages/types

**Files:**
- Create: `packages/types/package.json`
- Create: `packages/types/tsconfig.json`
- Create: `packages/types/src/common.ts`
- Create: `packages/types/src/user.ts`
- Create: `packages/types/src/auth.ts`
- Create: `packages/types/src/index.ts`

- [ ] **Step 1: Create packages/types/package.json**

```json
{
  "name": "@aio/types",
  "version": "0.0.1",
  "private": true,
  "main": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts"
  }
}
```

- [ ] **Step 2: Create packages/types/tsconfig.json**

```json
{
  "extends": "@aio/config/tsconfig",
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Create src/common.ts**

```typescript
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export type Locale = "ru" | "en";
```

- [ ] **Step 4: Create src/user.ts**

```typescript
export type UserRole = "user" | "admin" | "moderator";

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  telegram_id: number | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateUserPayload {
  full_name?: string;
  username?: string;
  avatar_url?: string;
}
```

- [ ] **Step 5: Create src/auth.ts**

```typescript
export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}

export interface TelegramAuthPayload {
  init_data: string;
}
```

- [ ] **Step 6: Create src/index.ts**

```typescript
export * from "./common";
export * from "./user";
export * from "./auth";
```

- [ ] **Step 7: Commit**

```bash
git add packages/types/
git commit -m "feat: add @aio/types shared TypeScript types"
```

---

### Task 4: packages/ui

**Files:**
- Create: `packages/ui/package.json`
- Create: `packages/ui/tsconfig.json`
- Create: `packages/ui/vitest.config.ts`
- Create: `packages/ui/src/lib/utils.ts`
- Create: `packages/ui/src/tokens/index.ts`
- Create: `packages/ui/src/components/button.tsx`
- Create: `packages/ui/src/components/input.tsx`
- Create: `packages/ui/src/components/card.tsx`
- Create: `packages/ui/src/components/badge.tsx`
- Create: `packages/ui/src/index.ts`
- Create: `packages/ui/tests/setup.ts`
- Create: `packages/ui/tests/button.test.tsx`

- [ ] **Step 1: Install ui package deps**

```bash
mkdir -p packages/ui && cd packages/ui
npm init -y
npm install react react-dom @radix-ui/react-slot class-variance-authority clsx tailwind-merge lucide-react
npm install -D typescript @types/react @types/react-dom vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom
```

- [ ] **Step 2: Create packages/ui/package.json**

```json
{
  "name": "@aio/ui",
  "version": "0.0.1",
  "private": true,
  "main": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts",
    "./tokens": "./src/tokens/index.ts"
  },
  "peerDependencies": {
    "react": "^18 || ^19",
    "react-dom": "^18 || ^19"
  },
  "scripts": {
    "test": "vitest run",
    "typecheck": "tsc --noEmit"
  }
}
```

- [ ] **Step 3: Create packages/ui/tsconfig.json**

```json
{
  "extends": "@aio/config/tsconfig",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["dom", "dom.iterable", "esnext"]
  },
  "include": ["src", "tests"]
}
```

- [ ] **Step 4: Create src/lib/utils.ts**

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 5: Create src/tokens/index.ts**

```typescript
// Swap CSS variables here to restyle the entire app
export const tokens = {
  colors: {
    primary: "hsl(var(--primary))",
    primaryForeground: "hsl(var(--primary-foreground))",
    secondary: "hsl(var(--secondary))",
    secondaryForeground: "hsl(var(--secondary-foreground))",
    background: "hsl(var(--background))",
    foreground: "hsl(var(--foreground))",
    muted: "hsl(var(--muted))",
    mutedForeground: "hsl(var(--muted-foreground))",
    border: "hsl(var(--border))",
    destructive: "hsl(var(--destructive))",
  },
  radius: {
    sm: "calc(var(--radius) - 4px)",
    md: "calc(var(--radius) - 2px)",
    lg: "var(--radius)",
    xl: "calc(var(--radius) + 4px)",
  },
} as const;
```

- [ ] **Step 6: Create src/components/button.tsx**

```typescript
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
```

- [ ] **Step 7: Create src/components/input.tsx**

```typescript
import * as React from "react";
import { cn } from "../lib/utils";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
```

- [ ] **Step 8: Create src/components/card.tsx**

```typescript
import * as React from "react";
import { cn } from "../lib/utils";

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)} {...props} />
  )
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
  )
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn("text-2xl font-semibold leading-none tracking-tight", className)} {...props} />
  )
);
CardTitle.displayName = "CardTitle";

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  )
);
CardContent.displayName = "CardContent";

export { Card, CardHeader, CardTitle, CardContent };
```

- [ ] **Step 9: Create src/components/badge.tsx**

```typescript
import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        destructive: "border-transparent bg-destructive text-destructive-foreground",
        outline: "text-foreground",
        success: "border-transparent bg-green-500 text-white",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
```

- [ ] **Step 10: Create src/index.ts**

```typescript
export * from "./components/button";
export * from "./components/input";
export * from "./components/card";
export * from "./components/badge";
export * from "./lib/utils";
export * from "./tokens";
```

- [ ] **Step 11: Create vitest.config.ts**

```typescript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
  },
});
```

- [ ] **Step 12: Create tests/setup.ts**

```typescript
import "@testing-library/jest-dom";
```

- [ ] **Step 13: Write failing test for Button**

Create `packages/ui/tests/button.test.tsx`:

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "../src/components/button";

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
  });

  it("applies destructive variant class", () => {
    render(<Button variant="destructive">Delete</Button>);
    expect(screen.getByRole("button").className).toContain("bg-destructive");
  });

  it("is disabled when disabled prop is set", () => {
    render(<Button disabled>Submit</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
```

- [ ] **Step 14: Run tests — expect FAIL (button not implemented yet)**

```bash
cd packages/ui
npm test
```

Expected: FAIL — module not found or component missing.

- [ ] **Step 15: Run tests again after all files created — expect PASS**

```bash
npm test
```

Expected: 3 tests pass.

- [ ] **Step 16: Commit**

```bash
git add packages/ui/
git commit -m "feat: add @aio/ui shared component library with design tokens"
```
