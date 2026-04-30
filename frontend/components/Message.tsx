type Role = "user" | "assistant" | "system";

export default function Message({ role, content }: { role: Role; content: string }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "bg-neutral-900 text-white dark:bg-white dark:text-neutral-900"
            : "bg-neutral-100 dark:bg-neutral-900"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
