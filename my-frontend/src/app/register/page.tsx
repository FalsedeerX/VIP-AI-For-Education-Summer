"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { postJson } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { Label } from "@/components/ui/label";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirm] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
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
      await postJson(
        "/users/register",
        { username, email, password, is_admin: isAdmin },
        false
      );
      await login(username, password);
      router.push("/");
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Registration failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col md:flex-row items-center justify-center bg-[var(--background)] p-4 space-y-6 md:space-y-0 md:space-x-5">
      {/* ── Registration Form ── */}
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-[var(--color-purdue-gold)] rounded-2xl shadow-lg p-8 space-y-6"
      >
        <h2 className="text-3xl font-bold text-center text-[var(--color-purdue-black)]">
          Sign Up
        </h2>

        {error && (
          <div className="text-red-600 text-sm bg-red-100 p-2 rounded">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {/** Username */}
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

          {/** Email */}
          <label className="block">
            {/*<span className="text-[var(--color-purdue-black)]">Email</span>*/}
            <Label
              className="text-[var(--color-purdue-black)] text-md"
              htmlFor="email"
            >
              Email
            </Label>
            <Input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="mt-1 bg-white text-black placeholder-gray-400"
            />
          </label>

          {/** Password */}
          <label className="block">
            <Label
              className="text-[var(--color-purdue-black)] text-md"
              htmlFor="password"
            >
              Password
            </Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="mt-1 bg-white text-black placeholder-gray-400"
            />
          </label>

          {/** Confirm Password */}
          <label className="block">
            <span className="text-[var(--color-purdue-black)]">
              Confirm Password
            </span>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirm(e.target.value)}
              required
              placeholder="••••••••"
              className="mt-1 bg-white text-black placeholder-gray-400"
            />
          </label>

          {/** Admin */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="admin"
              checked={isAdmin}
              onCheckedChange={(checked) => setIsAdmin(checked as boolean)}
              className="text-[var(--color-purdue-black)] bg-white"
            />
            <label htmlFor="admin" className="text-[var(--color-purdue-black)]">
              I am an admin
            </label>
          </div>

          {/** Terms and Conditions */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="terms"
              required
              className="text-[var(--color-purdue-black)] bg-white"
            />
            <label htmlFor="terms" className="text-[var(--color-purdue-black)]">
              I agree to the{" "}
              <Link
                href="/terms"
                className="text-[var(--color-purdue-blue)] underline style=cursor: pointer"
              >
                Terms and Conditions
              </Link>
            </label>
          </div>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold"
        >
          {loading ? "Signing up…" : "Sign Up"}
        </Button>
      </form>

      {/* ── Prompt box for existing users ── */}
      <div className="w-full max-w-sm bg-[var(--color-purdue-brown)] text-[var(--color-purdue-black)] rounded-2xl shadow-lg p-6 text-center space-y-4">
        <h3 className="text-xl font-semibold">Already registered?</h3>
        <p>Click below to sign in to your account.</p>
        <Link href="/login">
          <Button className="w-full bg-[var(--color-purdue-gold)] hover:opacity-90 text-[var(--color-purdue-black)]">
            Go to Log In
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
