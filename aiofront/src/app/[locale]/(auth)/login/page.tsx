"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

export default function LoginPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const res = await signIn("credentials", { email, password, redirect: false });
    if (res?.error) {
      setError(t("loginError"));
    } else {
      router.push("/dashboard");
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm rounded-xl border bg-card p-8 shadow">
        <h1 className="mb-6 text-2xl font-semibold">{t("loginTitle")}</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            placeholder={t("email")}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
          />
          <input
            type="password"
            placeholder={t("password")}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
          <button type="submit" className="rounded-md bg-primary px-4 py-2 text-primary-foreground">
            {t("login")}
          </button>
        </form>
      </div>
    </main>
  );
}
