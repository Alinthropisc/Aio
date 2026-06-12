export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
  pages: number;
}

export interface ErrorDetail {
  field: string | null;
  message: string;
}

export interface ApiError {
  success: false;
  code: string;
  message: string;
  errors: ErrorDetail[];
}

export interface SuccessResponse<T> {
  success: true;
  data: T | null;
}

export type Locale = "ru" | "en";
