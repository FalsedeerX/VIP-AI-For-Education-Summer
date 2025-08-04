// src/app/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      router.push("/");
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError("Login Failed");
      } else {
        setError("Invalid username or password. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col md:flex-row items-center justify-center bg-[var(--background)] p-4 space-y-6 md:space-y-0 md:space-x-6">
      {/* ── Sign-In Form ── */}
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-[var(--color-purdue-gold)] rounded-2xl shadow-lg p-8 space-y-6"
      >
        <h2 className="text-3xl font-bold text-center text-[var(--color-purdue-black)]">
          Log In
        </h2>

        {error && (
          <div className="text-red-600 text-sm bg-red-100 p-2 rounded">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <label className="block">
            <span className="text-[var(--color-purdue-black)]">Username</span>
            <Input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Your username"
              className="mt-1 bg-white text-black placeholder-gray-400"
            />
          </label>

          <label className="block">
            <span className="text-[var(--color-purdue-black)]">Password</span>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="mt-1 bg-white text-black placeholder-gray-400"
            />
          </label>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold"
        >
          {loading ? "Logging in…" : "Login"}
        </Button>
      </form>

      {/* ── Prompt for New Users ── */}
      <div className="w-full max-w-sm bg-[var(--color-purdue-brown)] text-[var(--color-purdue-black)] rounded-2xl shadow-lg p-6 text-center space-y-4">
        <h3 className="text-xl font-semibold">New here?</h3>
        <p>Click below to create an account.</p>
        <Link href="/register">
          <Button className="w-full bg-[var(--color-purdue-gold)] hover:opacity-90 text-[var(--color-purdue-black)]">
            Sign Up
          </Button>
        </Link>
        <div className="mt-8 flex justify-center">
          <Image
            //className="dark:invert"
            src="/PurduePete.png"
            alt="Purdue Pete"
            width={180}
            height={38}
            priority
          />
        </div>
      </div>
    </div>
  );
}
