"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/src/store/auth";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const { user, logout } = useAuthStore();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">{t("title")}</h1>
      <div className="mt-6 space-y-4">
        <div className="rounded-xl border bg-card p-6 shadow">
          <h2 className="text-xl font-semibold">{t("profile")}</h2>
          {user && (
            <p className="mt-2 text-muted-foreground">
              {user.username} · {user.email}
            </p>
          )}
        </div>
        <button
          onClick={handleLogout}
          className="rounded-md bg-destructive px-4 py-2 text-sm text-white"
        >
          Выйти
        </button>
      </div>
    </main>
  );
}
