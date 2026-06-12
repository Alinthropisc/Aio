"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { authApi } from "@/src/lib/api/auth";
import { useAuthStore } from "@/src/store/auth";

export default function RegisterPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const setTokens = useAuthStore((s) => s.setTokens);
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await authApi.register(form);
      if (res.success && res.data) {
        setTokens(res.data.access_token, res.data.refresh_token);
        router.push("/dashboard");
      }
    } catch {
      setError(t("loginError"));
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-sm rounded-xl border bg-card p-8 shadow">
        <h1 className="mb-6 text-2xl font-semibold">{t("registerTitle")}</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            placeholder={t("username")}
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
          />
          <input
            type="email"
            placeholder={t("email")}
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
          />
          <input
            type="password"
            placeholder={t("password")}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
          <button type="submit" className="rounded-md bg-primary px-4 py-2 text-primary-foreground">
            {t("register")}
          </button>
        </form>
      </div>
    </main>
  );
}
