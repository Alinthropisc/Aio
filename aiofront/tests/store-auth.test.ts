import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "../src/store/auth";

describe("useAuthStore", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  });

  it("sets tokens and marks authenticated", () => {
    useAuthStore.getState().setTokens("access123", "refresh456");
    const s = useAuthStore.getState();
    expect(s.accessToken).toBe("access123");
    expect(s.refreshToken).toBe("refresh456");
    expect(s.isAuthenticated).toBe(true);
  });

  it("sets user", () => {
    const user = { id: "1", username: "alice", email: "a@a.com", role: "user" as const, is_active: true, created_at: "", updated_at: "", full_name: null, telegram_id: null, avatar_url: null };
    useAuthStore.getState().setUser(user);
    expect(useAuthStore.getState().user).toEqual(user);
  });

  it("logout clears all auth state", () => {
    useAuthStore.getState().setTokens("t", "r");
    useAuthStore.getState().logout();
    const s = useAuthStore.getState();
    expect(s.accessToken).toBeNull();
    expect(s.isAuthenticated).toBe(false);
  });
});
