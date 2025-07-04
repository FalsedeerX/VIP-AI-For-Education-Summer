"use client"
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ChatScreen from "@/app/chatscreen";
import Sidebar2 from "@/components/ui/sidebar-2";


export default function ChatPage() {
	const params = useParams();
	const chatId = params?.chatId;

	return (
		<div className="flex flex-row flex-1 min-h-0 overflow-hidden bg-[var(--background)]">
        	<Sidebar2 />
        	<div className="flex flex-col flex-1 min-h-0 overflow-hidden">
          		<ChatScreen />
        	</div>
      	</div>
	);
}