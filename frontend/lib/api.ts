import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  saveTokens,
  type TokenPair,
} from "./auth";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ChatSession = { id: number; title: string; created_at: string };
export type Message = { id: number; role: "user" | "assistant" | "system"; content: string };
export type SessionDetail = ChatSession & { messages: Message[] };

type ServerTokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh_token = getRefreshToken();
  if (!refresh_token) return null;
  if (refreshing) return refreshing;
  refreshing = (async () => {
    const res = await fetch(`${API}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token }),
    });
    if (!res.ok) {
      clearTokens();
      return null;
    }
    const data = (await res.json()) as ServerTokenPair;
    saveTokens({ accessToken: data.access_token, refreshToken: data.refresh_token });
    return data.access_token;
  })().finally(() => {
    refreshing = null;
  });
  return refreshing;
}

async function authedFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let res = await fetch(`${API}${path}`, { ...init, headers });
  if (res.status === 401 && getRefreshToken()) {
    const fresh = await refreshAccessToken();
    if (fresh) {
      headers.set("Authorization", `Bearer ${fresh}`);
      res = await fetch(`${API}${path}`, { ...init, headers });
    }
  }
  return res;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const res = await authedFetch(path, { ...init, headers });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<TokenPair> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = (await res.json()) as ServerTokenPair;
  return { accessToken: data.access_token, refreshToken: data.refresh_token };
}

export async function register(email: string, password: string): Promise<void> {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || res.statusText);
  }
}

export async function logout(): Promise<void> {
  const refresh_token = getRefreshToken();
  clearTokens();
  if (!refresh_token) return;
  await fetch(`${API}/auth/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  }).catch(() => undefined);
}

export const listSessions = () => request<ChatSession[]>("/sessions/");
export const createSession = (title: string) =>
  request<ChatSession>("/sessions/", { method: "POST", body: JSON.stringify({ title }) });
export const getSession = (id: number) => request<SessionDetail>(`/sessions/${id}`);

export { authedFetch };
export const apiBase = API;
