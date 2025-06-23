// src/components/Header.tsx
"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import Image from "next/image";

export function Header() {
  return (
    <header className="w-full bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)] p-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        <Link href="/" className="hover:underline ">
          <Image
            //className="dark:invert"
            src="/Purdue_Boilermakers_logo.png"
            alt="Next.js logo"
            width={180}
            height={38}
            priority
          />
        </Link>
        <h1 className="text-4xl font-extrabold">PurdueGPT</h1>
      </div>
      <nav className="space-x-4">
        <Link href="/login" className="hover:underline ">
          <Button className="bg-purdue-black hover:opacity-90 text-purdue-gold font-semibold">
            Log In
          </Button>
        </Link>
        <Link href="/register" className="hover:underline">
          <Button className="bg-purdue-black hover:opacity-90 text-purdue-gold font-semibold">
            Sign up
          </Button>
        </Link>
      </nav>
    </header>
  );
}
