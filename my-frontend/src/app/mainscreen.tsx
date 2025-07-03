"use client";

import { useState } from "react";

export default function ChatScreen() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages([...messages, input]);
    setInput("");
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">

      {/* Message render area */}
      <div className="flex-1 overflow-y-auto bg-yellow-100 p-4 space-y-2">
        {messages.map((msg, i) => (
          <div
            key={i}
            className="bg-white p-2 rounded shadow text-black"
          >
            {msg}
          </div>
        ))}
      </div>

      {/* Input message box */}
      <div className="bg-green-600 p-2 flex gap-2">
        <input
          type="text"
          placeholder="Ask Anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 rounded text-black"
        />
        <button
          onClick={handleSend}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
}
