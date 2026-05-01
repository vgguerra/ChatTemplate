import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChatTemplate",
  description: "FastAPI + Next.js starter for chat apps with streaming, auth and persistent sessions",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100 antialiased">
        {children}
      </body>
    </html>
  );
}
