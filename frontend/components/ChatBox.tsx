"use client";

import { useEffect, useRef, useState } from "react";

import { getSession } from "@/lib/api";
import { useChatStream } from "@/lib/useChatStream";

import Message from "./Message";

type Msg = { id?: number; role: "user" | "assistant" | "system"; content: string };

export default function ChatBox({ sessionId }: { sessionId: number }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getSession(sessionId).then((s) => setMessages(s.messages ?? []));
  }, [sessionId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const { send } = useChatStream(sessionId, {
    onUserMessage: (content) =>
      setMessages((m) => [...m, { role: "user", content }, { role: "assistant", content: "" }]),
    onToken: (tok) =>
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = {
          ...copy[copy.length - 1],
          content: copy[copy.length - 1].content + tok,
        };
        return copy;
      }),
    onDone: () => setStreaming(false),
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;
    setStreaming(true);
    send(input);
    setInput("");
  };

  return (
    <>
      <div className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.map((m, i) => (
          <Message key={m.id ?? i} role={m.role} content={m.content} />
        ))}
        <div ref={endRef} />
      </div>
      <form
        onSubmit={onSubmit}
        className="border-t border-neutral-200 p-4 dark:border-neutral-800"
      >
        <div className="mx-auto flex max-w-3xl gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything..."
            className="flex-1 rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <button
            type="submit"
            disabled={streaming}
            className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-neutral-900"
          >
            Send
          </button>
        </div>
      </form>
    </>
  );
}
