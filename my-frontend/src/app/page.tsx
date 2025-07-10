// src/app/page.tsx
"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import MainScreen from "@/app/mainscreen";
import AdminDashboard from "./admindashboard";
import Sidebar from "@/components/ui/sidebar";

export default function Home() {
  const { name, loading, admin } = useAuth();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  if (loading) {
    return null;
  }

  if (admin) {
    // User is an admin, show admin dashboard
    return (
      <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
        <AdminDashboard />
      </div>
    );
  }

  if (name) {
    // User is logged in, show main screen
    return (
      <div className="flex flex-row flex-1 min-h-0 overflow-hidden bg-[var(--background)]">
        <Sidebar
          isDrawerOpen={isDrawerOpen}
          setIsDrawerOpen={setIsDrawerOpen}
        />
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
          <MainScreen />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
      <div className="max-w-md w-full bg-[var(--color-purdue-gold)] rounded-2xl shadow-lg p-8 space-y-6">
        <h2 className="text-3xl font-bold text-center text-[var(--color-purdue-black)]">
          Welcome to PurdueGPT
        </h2>

        <Image
          src="/PurduePete.png"
          alt="Purdue Pete"
          width={150}
          height={150}
          className="mx-auto mb-4"
        />

        <p className="text-center text-[var(--color-purdue-black)]">
          Please log in to continue or sign up for a new account.
        </p>

        <div className="flex justify-center space-x-4">
          <Link href="/login">
            <Button className="w-full bg-[var(--color-purdue-brown)] hover:opacity-90 text-[var(--color-purdue-black)]">
              Go to Log In
            </Button>
          </Link>
          <Link href="/register">
            <Button className="w-full bg-[var(--color-purdue-brown)] hover:opacity-90 text-[var(--color-purdue-black)]">
              Sign Up
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
