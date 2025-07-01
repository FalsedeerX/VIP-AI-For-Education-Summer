// src/app/page.tsx
"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
//import MainScreen from "@/app/mainscreen";
import ChatScreen from "@/app/chatscreen";
import AdminDashboard from "./admindashboard";
import Sidebar2 from "@/components/ui/sidebar-2";

export default function Home() {
  const { name, loading, admin } = useAuth();

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
    //return AdminDashboard();
  }

  if (name) {
    // User is logged in, show main screen
    return (
      <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
        <Sidebar2 />
      </div>
    ); /*
    return (
      <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
        <h1 className="text-4xl font-bold text-[var(--color-purdue-white)]">
          Welcome back, {name}!
        </h1>
      </div>
    );
    */
    //return MainScreen();
  }

  //return ChatScreen({ chatId: "2e7862c8-b538-4c82-994f-c1f8b535cb2b" });
  /*
    <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
      <h1 className="text-4xl font-bold text-[var(--color-purdue-white)]">
        Welcome back, !
      </h1>
    </div>
    */
  //}

  return (
    <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
      <div className="max-w-md w-full bg-[var(--color-purdue-gold)] rounded-2xl shadow-lg p-8 space-y-6">
        <h2 className="text-3xl font-bold text-center text-[var(--color-purdue-black)]">
          Welcome to PurdueGPT
        </h2>

        <Image
          src="/purdue_boilermakers_logo_mascot_2023_sportslogosnet-2378.png"
          alt="PurdueGPT Logo"
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
