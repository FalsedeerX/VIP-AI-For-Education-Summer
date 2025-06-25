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
  admin: boolean;
  name?: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  userId: null,
  name: null,
  admin: false,
  login: async () => {},
  logout: async () => {},
  loading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [admin, setAdmin] = useState(false); // Assuming admin state is needed
  const [name, setName] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        // note: response shape is { id, username }
        const { id, username, admin } = await getJson<{
          id: number;
          username: string;
          admin: boolean;
        }>("/users/me", true);
        setUserId(id);
        setName(username);
        setAdmin(admin); // Set admin state if needed
      } catch {
        setUserId(null);
        setName(null);
        setAdmin(false); // Reset admin state on error
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
    const { id, name, admin } = await getJson<{
      id: number;
      name: string;
      admin: boolean;
    }>("/users/me", true);
    setUserId(id);
    setName(name);
    setAdmin(admin); // Set admin state if needed
  }

  // 3) logout
  async function logout() {
    await getJson("/users/logout", true);
    setUserId(null);
    setName(null);
    setAdmin(false);
  }

  return (
    <AuthContext.Provider
      value={{ userId, name, admin, login, logout, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
