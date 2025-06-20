"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { postJson } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import "@/app/globals.css"; // Ensure global styles are imported

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await postJson("/users/register", { username, email, password }, false);
      router.push("/login");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-purdue-black p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-purdue-gold rounded-2xl shadow-lg p-8 space-y-6"
      >
        <h2 className="text-3xl font-bold text-purdue-black text-center">
          Sign Up
        </h2>

        {error && (
          <div className="text-red-600 text-sm bg-red-100 p-2 rounded">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <label className="block">
            <span className="text-purdue-black">Username</span>
            <Input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Your username"
              className="mt-1 bg-white text-purdue-black placeholder-gray-400"
            />
          </label>

          <label className="block">
            <span className="text-purdue-black">Email</span>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="mt-1 bg-white text-purdue-black placeholder-gray-400"
            />
          </label>

          <label className="block">
            <span className="text-purdue-black">Password</span>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="mt-1 bg-white text-purdue-black placeholder-gray-400"
            />
          </label>

          <label className="block">
            <span className="text-purdue-black">Confirm Password</span>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="mt-1 bg-white text-purdue-black placeholder-gray-400"
            />
          </label>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-purdue-black hover:opacity-90 text-purdue-gold font-semibold"
        >
          {loading ? "Signing up…" : "Sign Up"}
        </Button>
      </form>
    </div>
  );
}
