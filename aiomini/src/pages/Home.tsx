import { getTelegramUser } from "../lib/telegram";

export function HomePage() {
  const tgUser = getTelegramUser();
  return (
    <main className="p-4">
      <h1 className="text-2xl font-bold">Aio Mini</h1>
      {tgUser && (
        <p className="mt-1 text-muted-foreground">
          Привет, {tgUser.first_name}!
        </p>
      )}
    </main>
  );
}
