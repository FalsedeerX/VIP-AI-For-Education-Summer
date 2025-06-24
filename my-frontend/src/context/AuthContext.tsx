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

interface AuthContextType {
  userId: number | null;
  name?: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  userId: null,
  name: null,
  login: async () => {},
  logout: async () => {},
  loading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState<string | null>(null);

  // 1) On mount, fetch /users/me
  useEffect(() => {
    (async () => {
      try {
        // note: response shape is { id, username }
        const { id, username } = await getJson<{
          id: number;
          username: string;
        }>("/users/me", true);
        setUserId(id);
        setName(username);
      } catch {
        setUserId(null);
        setName(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // 2) login → POST /users/auth → GET /users/me
  async function login(username: string, password: string) {
    await postJson<{ success: boolean }>(
      "/users/auth",
      { username, password },
      true
    );

    // now re-fetch the “me” endpoint
    const { id } = await getJson<{ id: number; username: string }>(
      "/users/me",
      true
    );
    setUserId(id);
    setName(username);
  }

  // 3) logout
  async function logout() {
    await getJson("/users/logout", true);
    setUserId(null);
    setName(null);
  }

  return (
    <AuthContext.Provider value={{ userId, name, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
