"use client";
import { getJson, postJson } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useEffect, useState, useRef } from "react";
import TextareaAutosize from "react-textarea-autosize";

type Message = {
  user_id: number;
  message: string;
  created_at: number;
};

type UserInfo = {
  id: number;
  username: string;
  admin: boolean;
}


export default function ChatScreen( {chatId} : {chatId: string} ) {
  const socketRef = useRef<WebSocket | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");


  // auto setup upon initial render
  useEffect(() => {
    async function fetchChatLog() {
      try {
        const messages = await getJson<Message[]>(`/chats/${chatId}`, {}, true);
        setMessages(messages);
      } catch {}
    }

    async function fetchUserInfo() {
      try {
        const info = await getJson<UserInfo>("/users/me", {}, true);
        setUserInfo(info);
      } catch {}
    }

    // initial websocket connecttion & fetch previous chat logs
    const socket = new WebSocket(`ws://localhost:8000/chats/relay/${chatId}`);
    socket.onmessage = handleRecv;
    socketRef.current = socket;
    fetchChatLog();
    fetchUserInfo();

    // websocket cleanup
    return () => { socket.close() };
  }, []);


  // send message to backend's AI model
  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages((prev) => [...prev, { user_id: userInfo.id, message: input, created_at: Date.now() }]);
    socketRef.current?.send(input);
    setInput("");
  };


  // receive response from backend's AI model
  const handleRecv = (event: MessageEvent) => {
    const response = event.data;
    setMessages((prev) => [...prev, { user_id: -1, message: response, created_at: Date.now() }]);
  };


  return (
    <div className="flex flex-col flex-1 min-h-0">

      {/* Message Display area */}
      <div className="flex-1 overflow-y-auto bg-[var(--color-chat-background)] p-4 space-y-6">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[50%] p-3 rounded-lg whitespace-pre-wrap ${
              msg.user_id !== -1
                ? "ml-auto bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)]"
                : "mr-auto bg-white text-black shadow"
            }`}
          >
            {msg.message}
          </div>
        ))}
      </div>

      {/* User Message Input Box */}
      <div className="flex bg-[var(--color-chat-background)] p-4 justify-center">
        <div className="w-full max-w-2xl flex gap-2 items-end">
          <TextareaAutosize
            placeholder="Ask Anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            minRows={1}
            maxRows={8}
            className="flex-1 resize-none p-3 rounded-lg text-white bg-[#2E2E38] placeholder-gray-400 border border-gray-600 focus:outline-none"
          />

          <Button
            onClick={handleSend}
            className="bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)] px-4 py-2 rounded-full"
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
