// src/components/Header.tsx
"use client";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export function Header() {
  const { name, logout } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function handleLogout(e: React.FormEvent) {
    e.preventDefault();
    try {
      logout();
      router.push("/login");
    } catch (err: any) {
      setError(err.message || "Logout failed");
    }
  }

  return (
    <header className="w-full bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)] p-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        <Link href="/">
          <Image
            src="/Purdue_Boilermakers_logo.png"
            alt="Boilermakers logo"
            width={180}
            height={38}
            priority
          />
        </Link>
        <h1 className="text-4xl font-extrabold">PurdueGPT</h1>
      </div>

      <nav className="space-x-4">
        {!name ? (
          <>
            <Link href="/login">
              <Button
                variant="purdue"
                className="bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)] hover:bg-[var(--color-purdue-black)]/90"
              >
                Log In
              </Button>
            </Link>
            <Link href="/register">
              <Button
                variant="purdue"
                className="bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)] hover:bg-[var(--color-purdue-black)]/90"
              >
                Sign Up
              </Button>
            </Link>
          </>
        ) : (
          <form onSubmit={handleLogout} className="inline">
            <Button
              type="submit"
              variant="purdue"
              className="bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)] hover:bg-[var(--color-purdue-black)]/90"
            >
              Log Out
            </Button>
          </form>
        )}
      </nav>
    </header>
  );
}
