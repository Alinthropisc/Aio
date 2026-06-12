export type UserRole = "user" | "admin" | "moderator";

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  telegram_id: number | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateUserPayload {
  full_name?: string;
  username?: string;
  avatar_url?: string;
}
