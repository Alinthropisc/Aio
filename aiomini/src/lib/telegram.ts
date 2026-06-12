import WebApp from "@twa-dev/sdk";

export const tg = WebApp;

export function initTelegram() {
  tg.ready();
  tg.expand();
}

export function getTelegramUser() {
  return tg.initDataUnsafe?.user ?? null;
}

export function closeMiniApp() {
  tg.close();
}

export function showAlert(message: string) {
  tg.showAlert(message);
}
