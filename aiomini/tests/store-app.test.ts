import { describe, it, expect, beforeEach } from "vitest";
import { useAppStore } from "../src/store/app";

describe("useAppStore", () => {
  beforeEach(() => {
    useAppStore.setState({ user: null, accessToken: null, locale: "ru" });
  });

  it("sets token", () => {
    useAppStore.getState().setToken("tok123");
    expect(useAppStore.getState().accessToken).toBe("tok123");
  });

  it("switches locale", () => {
    useAppStore.getState().setLocale("en");
    expect(useAppStore.getState().locale).toBe("en");
  });

  it("logout clears user and token", () => {
    useAppStore.getState().setToken("tok");
    useAppStore.getState().logout();
    expect(useAppStore.getState().accessToken).toBeNull();
    expect(useAppStore.getState().user).toBeNull();
  });
});
