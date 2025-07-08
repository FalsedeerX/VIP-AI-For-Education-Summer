"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { getJson, postJson } from "@/lib/api";
import TextareaAutosize from "react-textarea-autosize";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

type Message = {
  user_id: number;
  message: string;
  created_at: number;
};
type UserInfo = {
  id: number;
  username: string;
  admin: boolean;
};

const MessageBubble = ({ msg, isOwn }: { msg: Message; isOwn: boolean }) => {
  const time = new Date(msg.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  return (
    <div
      className={`max-w-[60%] p-3 rounded-lg whitespace-pre-wrap relative ${
        isOwn
          ? "ml-auto bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)]"
          : "mr-auto bg-white text-black shadow"
      }`}
    >
      <div>{msg.message}</div>
      <span className="absolute bottom-1 right-2 text-xs opacity-60">
        {time}
      </span>
    </div>
  );
};

export default function ChatScreen({ chatId }: { chatId: string }) {
  const socketRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialize socket connection + fetch data
  useEffect(() => {
    let socket: WebSocket;

    async function init() {
      try {
        const [msgs, info] = await Promise.all([
          getJson<Message[]>(`/chats/${chatId}`, true),
          getJson<UserInfo>("/users/me", true),
        ]);
        console.log("Fetched messages:", msgs);
        console.log("Fetched user info:", info);
        setMessages(msgs);
        setUserInfo(info);
      } catch (err) {
        console.error("Fetch error", err);
      }

      socket = new WebSocket(`ws://localhost:8000/chats/relay/${chatId}`);
      socket.onopen = () => setIsConnected(true);
      socket.onclose = () => setIsConnected(false);
      socket.onerror = (e) => console.error("WebSocket error", e);
      socket.onmessage = (e) => {
        setMessages((prev) => [
          ...prev,
          { user_id: -1, message: e.data, created_at: Date.now() },
        ]);
      };
      socketRef.current = socket;
    }

    init();

    return () => {
      socketRef.current?.close();
    };
  }, [chatId]);

  const handleSend = useCallback(() => {
    console.log("Sending message:", !input.trim());
    console.log("isConnected:", !isConnected);
    console.log("userInfo:", !userInfo);
    if (!input.trim() || !isConnected || !userInfo) return;
    console.log("Sending message:", input.trim());
    const outgoing: Message = {
      user_id: userInfo.id,
      message: input.trim(),
      created_at: Date.now(),
    };
    // echo locally
    setMessages((prev) => [...prev, outgoing]);
    socketRef.current?.send(input.trim());
    setInput("");
  }, [input, isConnected, userInfo]);

  // Send on Enter (⇧+Enter = newline)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-[var(--color-chat-background)] p-4 space-y-4">
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            msg={msg}
            isOwn={msg.user_id === userInfo?.id}
          />
        ))}
        <div ref={bottomRef} />
      </div>

      <Separator className="bg-[var(--color-purdue-gold)]" />

      {/* Input & Send */}
      <div className="flex bg-[var(--color-chat-background)] p-4 justify-center">
        <div className="w-full max-w-2xl flex gap-2 items-end">
          <TextareaAutosize
            placeholder="Ask anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            minRows={1}
            maxRows={6}
            className="flex-1 resize-none p-3 rounded-lg text-white bg-[#2E2E38] placeholder-gray-400 border border-gray-600 focus:outline-none"
          />

          <Button
            onClick={handleSend}
            disabled={!input.trim() || !isConnected}
            className="bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)] h-full self-stretch"
          >
            Send
          </Button>
        </div>
      </div>

      <div className="text-[var(--color-purdue-gray)] text-xs text-center p-2 bg-[var(--color-chat-background)] mb-2">
        {isConnected ? (
          "Purdue AI is ready—press Enter to send"
        ) : (
          <>
            <span>Disconnected. </span>
            <Button
              variant="link"
              size="sm"
              onClick={() => window.location.reload()}
            >
              Reconnect?
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
