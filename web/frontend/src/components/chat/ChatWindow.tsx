"use client";

import { useEffect, useRef } from "react";
import { useSessionStore } from "@/store/sessionStore";
import MessageBubble from "./MessageBubble";
import { Loader2 } from "lucide-react";

export default function ChatWindow() {
  const messages = useSessionStore((s) => s.messages);
  const isStreaming = useSessionStore((s) => s.isStreaming);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 dark:text-gray-600">
        <div className="text-center">
          <p className="text-lg font-medium">MD Simulation Agent</p>
          <p className="text-sm mt-1">Describe your simulation or ask about a paper</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {isStreaming && (
        <div className="flex gap-3 px-4 py-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-orange-400 to-rose-500 text-white text-xs font-bold flex-shrink-0">
            AI
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <Loader2 size={14} className="animate-spin" />
            <span className="text-sm">Thinking…</span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
