"use client";

import { useState, useEffect, useRef, FormEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
}

interface ChatScreenProps {
  chatId: string;
}

export default function ChatScreen({ chatId }: ChatScreenProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Fetch existing messages
  useEffect(() => {
    async function loadMessages() {
      try {
        const res = await fetch(`/chats/${chatId}`);
        if (!res.ok) throw new Error("Failed to load messages");
        const data = await res.json(); // assumes { messages: [{ id, sender, text }] }
        setMessages(
          data.messages.map((m: any) => ({
            id: m.id,
            sender: m.sender,
            text: m.text,
          }))
        );
      } catch (e) {
        console.error(e);
      }
    }
    loadMessages();
  }, [chatId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: newMessage.trim(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setNewMessage("");

    // send to backend
    fetch(`/chats/${chatId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg.text }),
    }).catch(console.error);

    // simulate AI response
    setTimeout(() => {
      const botMsg: Message = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: "This is a simulated AI response. Replace with real API call soon.",
      };
      setMessages((prev) => [...prev, botMsg]);

      // optionally log bot message
      fetch(`/chats/${chatId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: botMsg.text }),
      }).catch(console.error);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`max-w-xs md:max-w-md lg:max-w-lg p-3 rounded-2xl break-words whitespace-pre-wrap ${
              msg.sender === "user"
                ? "self-end bg-blue-600 text-white rounded-br-none"
                : "self-start bg-gray-200 text-gray-800 rounded-bl-none"
            }`}
          >
            {msg.text}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSend} className="flex items-center border-t p-3">
        <Input
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          className="flex-1 mr-2"
        />
        <Button
          className="w bg-[var(--color-purdue-gold)] hover:opacity-90 text-[var(--color-purdue-black)]"
          type="submit"
        >
          Send
        </Button>
      </form>
    </div>
  );
}
