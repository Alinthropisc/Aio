"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/src/lib/api/users";

export default function AdminPage() {
  const t = useTranslations("admin");
  const { data, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersApi.list(),
  });

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">{t("title")}</h1>
      <div className="mt-6 rounded-xl border bg-card p-6 shadow">
        <h2 className="text-xl font-semibold">{t("users")}</h2>
        {isLoading && <p className="mt-2 text-muted-foreground">Loading...</p>}
        {data?.data && (
          <p className="mt-2 text-muted-foreground">
            {t("totalUsers")}: {data.data.total}
          </p>
        )}
      </div>
    </main>
  );
}
