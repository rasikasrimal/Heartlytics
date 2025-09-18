"use client";

import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";

import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/types/chat";

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

const iconMap = {
  assistant: Bot,
  user: User,
  system: Bot
};

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const Icon = iconMap[message.author];
  const isUser = message.author === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn("flex gap-3", isUser && "flex-row-reverse")}
    >
      <span
        className={cn(
          "mt-1 flex h-8 w-8 items-center justify-center rounded-full shadow-sm",
          isUser ? "bg-secondary text-secondary-foreground" : "bg-muted text-muted-foreground"
        )}
      >
        <Icon className="h-4 w-4" />
      </span>
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-5 py-3 text-sm leading-6",
          isUser
            ? "bg-secondary text-secondary-foreground"
            : "bg-muted text-muted-foreground shadow-sm"
        )}
      >
        <p className="whitespace-pre-wrap text-sm leading-6">{message.content || ""}</p>
        {message.streaming && (
          <span className="mt-2 inline-flex items-center gap-1 text-xs text-muted-foreground">
            <span className="h-2 w-2 animate-pulse rounded-full bg-accent" />
            streaming
          </span>
        )}
      </div>
    </motion.div>
  );
}
