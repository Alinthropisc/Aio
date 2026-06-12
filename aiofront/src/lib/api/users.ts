import type { User, UpdateUserPayload, PaginatedResponse, SuccessResponse } from "@aio/types";
import { apiClient } from "./client";

export const usersApi = {
  getMe: () =>
    apiClient.get<SuccessResponse<User>>("/api/v1/users/me").then((r) => r.data),

  updateMe: (data: UpdateUserPayload) =>
    apiClient.patch<SuccessResponse<User>>("/api/v1/users/me", data).then((r) => r.data),

  list: (params?: { limit?: number; offset?: number }) =>
    apiClient
      .get<SuccessResponse<PaginatedResponse<User>>>("/api/v1/users", { params })
      .then((r) => r.data),

  getById: (id: string) =>
    apiClient.get<SuccessResponse<User>>(`/api/v1/users/${id}`).then((r) => r.data),

  deleteById: (id: string) =>
    apiClient.delete(`/api/v1/users/${id}`).then((r) => r.data),
};
