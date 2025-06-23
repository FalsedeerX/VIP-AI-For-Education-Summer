// src/context/AuthContext.tsx
"use client";
import React, {
  createContext,
  useState,
  useContext,
  ReactNode,
  useEffect,
} from "react";
import { postJson, getJson } from "../lib/api";
const API_BASE = "http://127.0.0.1:8000";

interface AuthContextType {
  userId: number | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  userId: null,
  login: async () => {},
  logout: async () => {},
  loading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // Bootstrap on mount (GET /users/me)
  useEffect(() => {
    (async () => {
      try {
        const { user_id } = await getJson<{ user_id: number }>(
          "/users/me",
          true
        );
        setUserId(user_id);
      } catch {
        setUserId(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // login() → POST /users/auth → GET /users/me
  async function login(username: string, password: string) {
    await postJson<{ success: boolean }>(
      "/users/auth",
      { username, password },
      true
    );
    const { user_id } = await getJson<{ user_id: number }>("/users/me", true);
    setUserId(user_id);
  }

  async function logout() {
    await postJson("/users/logout", {}, true);
    setUserId(null);
  }

  return (
    <AuthContext.Provider value={{ userId, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
