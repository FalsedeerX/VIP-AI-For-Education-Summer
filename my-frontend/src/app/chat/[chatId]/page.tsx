// ChatPage.tsx
"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ChatScreen from "@/app/chatscreen";
import Sidebar from "@/components/ui/sidebar";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function ChatPage() {
  const params = useParams();
  const chatId = typeof params?.chatId === "string" ? params.chatId : "";
  const router = useRouter();
  const { userId, loading } = useAuth();
  // lift open state up so ChatPage can also adjust the content area
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  useEffect(() => {
    if (!loading && !userId) {
      router.replace("/login");
    }
  }, [loading, userId, router]);

  // 2) While we’re checking auth (or before redirect), render nothing
  if (loading || !userId) {
    return null;
  }

  return (
    <div className="flex h-full min-h-0 bg-[var(--background)] overflow-hidden">
      <Sidebar isDrawerOpen={isDrawerOpen} setIsDrawerOpen={setIsDrawerOpen} />
      <div className="flex-1 min-h-0 min-w-0 overflow-hidden">
        <ChatScreen chatId={chatId} />
      </div>
    </div>
  );
}
