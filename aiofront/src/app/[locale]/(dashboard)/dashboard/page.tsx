"use client";

import { useTranslations } from "next-intl";
import { useAuthStore } from "@/src/store/auth";

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const user = useAuthStore((s) => s.user);
  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">{t("title")}</h1>
      {user && <p className="mt-2 text-muted-foreground">{t("welcome", { name: user.username })}</p>}
    </main>
  );
}
