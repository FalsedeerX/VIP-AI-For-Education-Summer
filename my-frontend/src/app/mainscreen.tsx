
//   return (
//     <div className="flex flex-col flex-1 min-h-0">
//       {/* 🟨 Scrollable Message Area */}
//       <div className="flex-1 overflow-y-auto bg-[#202123] p-4 space-y-4">
//         {messages.map((msg, i) => (
//           <div
//             key={i}
//             className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
//           >
//             <div
//               className={`px-4 py-2 rounded-2xl max-w-[75%] break-words ${
//                 msg.role === "user"
//                   ? "bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)]"
//                   : "bg-[#343541] text-white"
//               }`}
//             >
//               {msg.content}
//             </div>
//           </div>
//         ))}
//       </div>

//       {/* 🔻 Input Footer */}
//       <div className="bg-[#202123] p-4 flex justify-center border-t border-gray-600">
//         <div className="w-2/3 flex gap-2 items-end">
//           <TextareaAutosize
//             placeholder="Ask Anything..."
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             minRows={1}
//             maxRows={8}
//             className="flex-1 p-3 rounded-lg text-white bg-[#2E2E38] placeholder-gray-400 border border-gray-600 focus:outline-none resize-none"
//           />
//           <Button
//             onClick={handleSend}
//             className="bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)] px-4 py-2 rounded-full"
//           >
//             Send
//           </Button>
//         </div>
//       </div>
//     </div>
//   );
// }

"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import TextareaAutosize from "react-textarea-autosize";

// custom type for holding message
type Message = {
  role: "user" | "AI";
  content: string;
};


export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  // send the user input message to backend
  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    setInput("");

    // mimic AI generated response
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "AI", content: "Working on it..." }]);
    }, 500);
  };

  // Fetch previous chat log from backend upon page render
  useEffect(() => {
    async function fetchChatLog() {
      const rawMessages = [
        "Hello!",
        "Hi there! How can I help you today?",
        "What is AI?",
        "AI stands for Artificial Intelligence..."
      ];

      const formatted: Message[] = rawMessages.map((msg, i) => ({
        role: i % 2 === 0 ? "user" : "assistant",
        content: msg,
      }));

      setMessages(formatted);
    }

    fetchChatLog();
  }, []);


  return (
    <div className="flex flex-col flex-1 min-h-0">

      {/* Message Display area */}
      <div className="flex-1 overflow-y-auto bg-[var(--color-chat-background)] p-4 space-y-6">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[50%] p-3 rounded-lg whitespace-pre-wrap ${
              msg.role === "user"
                ? "ml-auto bg-[var(--color-purdue-black)] text-[var(--color-purdue-gold)]"
                : "mr-auto bg-white text-black shadow"
            }`}
          >
            {msg.content}
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
