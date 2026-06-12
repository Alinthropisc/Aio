import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { authApi } from "@/src/lib/api/auth";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      authorize: async (credentials) => {
        const parsed = loginSchema.safeParse(credentials);
        if (!parsed.success) return null;
        try {
          const res = await authApi.login({
            email: parsed.data.email,
            password: parsed.data.password,
          });
          if (!res.success || !res.data) return null;
          return {
            id: "session",
            accessToken: res.data.access_token,
            refreshToken: res.data.refresh_token,
          };
        } catch {
          return null;
        }
      },
    }),
  ],
  callbacks: {
    jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as { accessToken: string }).accessToken;
        token.refreshToken = (user as { refreshToken: string }).refreshToken;
      }
      return token;
    },
    session({ session, token }) {
      (session as { accessToken?: string }).accessToken = token.accessToken as string;
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
});
