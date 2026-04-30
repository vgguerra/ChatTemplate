"use client";

import { useEffect, useState } from "react";

import ChatBox from "@/components/ChatBox";
import { createSession, listSessions, type ChatSession } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [needsAuth, setNeedsAuth] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      setNeedsAuth(true);
      return;
    }
    listSessions()
      .then((s) => {
        setSessions(s);
        if (s[0]) setActiveId(s[0].id);
      })
      .catch(() => setNeedsAuth(true));
  }, []);

  const onNew = async () => {
    const s = await createSession("New chat");
    setSessions((prev) => [s, ...prev]);
    setActiveId(s.id);
  };

  if (needsAuth) {
    return (
      <main className="mx-auto max-w-md p-8">
        Please <a href="/login" className="underline">sign in</a> first.
      </main>
    );
  }

  return (
    <main className="grid h-screen grid-cols-[260px_1fr]">
      <aside className="border-r border-neutral-200 p-4 dark:border-neutral-800">
        <button
          onClick={onNew}
          className="mb-4 w-full rounded-md bg-neutral-900 px-3 py-2 text-sm font-medium text-white dark:bg-white dark:text-neutral-900"
        >
          + New chat
        </button>
        <ul className="space-y-1">
          {sessions.map((s) => (
            <li key={s.id}>
              <button
                onClick={() => setActiveId(s.id)}
                className={`w-full rounded-md px-3 py-2 text-left text-sm ${
                  s.id === activeId
                    ? "bg-neutral-200 dark:bg-neutral-800"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-900"
                }`}
              >
                {s.title}
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <section className="flex flex-col">
        {activeId ? (
          <ChatBox sessionId={activeId} />
        ) : (
          <div className="m-auto text-neutral-500">Create a session to start.</div>
        )}
      </section>
    </main>
  );
}
