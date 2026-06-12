import { useTranslations } from "next-intl";
import Link from "next/link";

export default function HomePage() {
  const t = useTranslations("nav");
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-4xl font-bold">Aio</h1>
      <p className="text-muted-foreground text-lg">Full-Stack Starter Template</p>
      <div className="flex gap-4">
        <Link href="/login" className="rounded-md bg-primary px-6 py-2 text-primary-foreground">
          {t("dashboard")}
        </Link>
      </div>
    </main>
  );
}
