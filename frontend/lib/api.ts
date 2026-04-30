import { getToken } from "./auth";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ChatSession = { id: number; title: string; created_at: string };
export type Message = { id: number; role: "user" | "assistant" | "system"; content: string };
export type SessionDetail = ChatSession & { messages: Message[] };

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = (await res.json()) as { access_token: string };
  return data.access_token;
}

export async function register(email: string, password: string): Promise<void> {
  await request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export const listSessions = () => request<ChatSession[]>("/sessions/");
export const createSession = (title: string) =>
  request<ChatSession>("/sessions/", { method: "POST", body: JSON.stringify({ title }) });
export const getSession = (id: number) => request<SessionDetail>(`/sessions/${id}`);

export const apiBase = API;
