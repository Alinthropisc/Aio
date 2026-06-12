import { describe, it, expect, vi, beforeEach } from "vitest";
import { authApi } from "../src/lib/api/auth";
import { apiClient } from "../src/lib/api/client";

vi.mock("../src/lib/api/client", () => ({
  apiClient: { post: vi.fn() },
}));

const mockPost = vi.mocked(apiClient.post);

beforeEach(() => vi.clearAllMocks());

describe("authApi", () => {
  it("login calls correct endpoint and returns data", async () => {
    const tokens = { access_token: "a", refresh_token: "r", token_type: "bearer" };
    mockPost.mockResolvedValueOnce({ data: { success: true, data: tokens } });
    const res = await authApi.login({ email: "a@a.com", password: "pass" });
    expect(mockPost).toHaveBeenCalledWith("/api/v1/auth/login", { email: "a@a.com", password: "pass" });
    expect(res.data).toEqual(tokens);
  });

  it("register calls correct endpoint", async () => {
    mockPost.mockResolvedValueOnce({ data: { success: true, data: {} } });
    await authApi.register({ username: "alice", email: "a@a.com", password: "pass" });
    expect(mockPost).toHaveBeenCalledWith("/api/v1/auth/register", expect.objectContaining({ email: "a@a.com" }));
  });
});
