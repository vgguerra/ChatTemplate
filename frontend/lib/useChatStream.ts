"use client";

import { useCallback } from "react";

import { apiBase } from "./api";
import { getToken } from "./auth";

type Handlers = {
  onUserMessage?: (content: string) => void;
  onToken?: (token: string) => void;
  onDone?: () => void;
  onError?: (err: unknown) => void;
};

/**
 * Consumes the SSE stream from POST /chat/{sessionId}/stream.
 * fetch + ReadableStream parser (EventSource doesn't support custom headers).
 */
export function useChatStream(sessionId: number, handlers: Handlers) {
  const send = useCallback(
    async (message: string) => {
      handlers.onUserMessage?.(message);
      try {
        const res = await fetch(`${apiBase}/chat/${sessionId}/stream`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken() ?? ""}`,
            Accept: "text/event-stream",
          },
          body: JSON.stringify({ message }),
        });
        if (!res.body) throw new Error("No stream body");

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split("\n\n");
          buffer = events.pop() ?? "";
          for (const evt of events) {
            const lines = evt.split("\n");
            const event = lines.find((l) => l.startsWith("event:"))?.slice(6).trim();
            const data = lines.find((l) => l.startsWith("data:"))?.slice(5) ?? "";
            if (event === "token") handlers.onToken?.(data);
            else if (event === "done") handlers.onDone?.();
          }
        }
        handlers.onDone?.();
      } catch (e) {
        handlers.onError?.(e);
        handlers.onDone?.();
      }
    },
    [sessionId, handlers],
  );

  return { send };
}
