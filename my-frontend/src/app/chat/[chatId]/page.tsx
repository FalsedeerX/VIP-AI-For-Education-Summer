// ChatPage.tsx
"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ChatScreen from "@/app/chatscreen";
import Sidebar from "@/components/ui/sidebar";

export default function ChatPage() {
  const params = useParams();
  const chatId = typeof params?.chatId === "string" ? params.chatId : "";

  // lift open state up so ChatPage can also adjust the content area
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <div className="flex h-full min-h-0 bg-[var(--background)] overflow-hidden">
      <Sidebar isDrawerOpen={isDrawerOpen} setIsDrawerOpen={setIsDrawerOpen} />
      <div className="flex-1 min-h-0 min-w-0 overflow-hidden">
        <ChatScreen chatId={chatId} />
      </div>
    </div>
  );
}
