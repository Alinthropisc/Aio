import { useAppStore } from "../store/app";

export function SettingsPage() {
  const { locale, setLocale } = useAppStore();
  return (
    <main className="p-4">
      <h1 className="text-2xl font-bold">Настройки</h1>
      <div className="mt-4 rounded-xl border bg-card p-4">
        <p className="text-sm font-medium text-muted-foreground">Язык / Language</p>
        <div className="mt-2 flex gap-2">
          {(["ru", "en"] as const).map((l) => (
            <button
              key={l}
              onClick={() => setLocale(l)}
              className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                locale === l
                  ? "bg-primary text-primary-foreground"
                  : "border border-input bg-background hover:bg-accent"
              }`}
            >
              {l === "ru" ? "Русский" : "English"}
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
