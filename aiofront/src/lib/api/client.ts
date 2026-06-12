import axios from "axios";
import type { ApiError } from "@aio/types";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    const apiError: ApiError = error.response?.data ?? {
      success: false,
      code: "NETWORK_ERROR",
      message: error.message,
      errors: [],
    };
    return Promise.reject(apiError);
  }
);
