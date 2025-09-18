import { memo } from "react";

import { cn, formatRelativeTime } from "@/lib/utils";
import type { ChatMessage } from "@/types/chat";

interface ChatMessageProps {
  message: ChatMessage;
}

export const ChatMessageBubble = memo(function ChatMessageBubble({ message }: ChatMessageProps) {
  const isAssistant = message.author === "assistant";

  return (
    <div className={cn("flex flex-col gap-2", isAssistant ? "items-start" : "items-end")}> 
      <div
        className={cn(
          "max-w-[90%] rounded-2xl border px-4 py-3 text-sm shadow-sm",
          isAssistant
            ? "border-border/70 bg-card/90 text-foreground"
            : "border-primary/40 bg-primary text-primary-foreground"
        )}
      >
        {message.content || (message.streaming ? "…" : "")}
      </div>
      <span className="text-xs uppercase tracking-wide text-muted-foreground">
        {isAssistant ? "Heartlytics" : "You"} · {formatRelativeTime(message.createdAt)}
      </span>
    </div>
  );
});
