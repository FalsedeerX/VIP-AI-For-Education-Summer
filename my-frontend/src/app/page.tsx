import Image from "next/image";
import { useAuth } from "@/context/AuthContext";

export default function Home() {
  const { userId } = useAuth();
  if (userId) {
    return (
      <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
        <h1 className="text-3xl font-bold text-[var(--color-purdue-black)]">
          Welcome, {userId}!
        </h1>
      </div>
    );
  }
  return (
    <div className="flex flex-1 items-center justify-center bg-[var(--background)] p-4">
      <div className="max-w-md w-full bg-[var(--color-purdue-gold)] rounded-2xl shadow-lg p-8 space-y-6">
        <h2 className="text-3xl font-bold text-center text-[var(--color-purdue-black)]">
          Welcome to My App
        </h2>
        <p className="text-center text-[var(--color-purdue-black)]">
          Please log in to continue.
        </p>
        <Image
          src="/images/logo.png"
          alt="Logo"
          width={150}
          height={150}
          className="mx-auto mb-4"
        />
        <p className="text-center text-[var(--color-purdue-black)]">
          This is a placeholder page. Please log in to access the application.
        </p>
        <p className="text-center text-[var(--color-purdue-black)]">
          <a
            href="/login"
            className="text-[var(--color-purdue-black)] underline hover:text-[var(--color-purdue-black)]"
          >
            Go to Login
          </a>
        </p>
      </div>
    </div>
  );
}
