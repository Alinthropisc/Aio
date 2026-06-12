import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@aio/types";

interface AppState {
  user: User | null;
  accessToken: string | null;
  locale: "ru" | "en";
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  setLocale: (locale: "ru" | "en") => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      locale: "ru",
      setUser: (user) => set({ user }),
      setToken: (token) => set({ accessToken: token }),
      setLocale: (locale) => set({ locale }),
      logout: () => set({ user: null, accessToken: null }),
    }),
    { name: "aio-mini", partialize: (s) => ({ locale: s.locale, accessToken: s.accessToken }) }
  )
);
