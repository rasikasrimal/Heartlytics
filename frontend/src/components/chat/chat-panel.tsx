"use client";

import { useMemo } from "react";

import { ChatInput } from "@/components/chat/chat-input";
import { ChatMessageBubble } from "@/components/chat/chat-message-bubble";
import { ChatMessageSkeleton } from "@/components/skeletons/chat-message-skeleton";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatStore } from "@/stores/use-chat-store";

export function ChatPanel() {
  const messages = useChatStore((state) => state.messages);
  const isStreaming = useChatStore((state) => state.isStreaming);

  const sortedMessages = useMemo(
    () => [...messages].sort((a, b) => a.createdAt - b.createdAt),
    [messages]
  );

  return (
    <Card className="flex h-[540px] flex-col overflow-hidden border-border/80 bg-card/70 p-0">
      <div className="flex items-center justify-between border-b border-border/80 px-6 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
            Conversation
          </p>
          <p className="text-sm text-muted-foreground">
            Streaming enabled • Multi-turn context preserved
          </p>
        </div>
      </div>
      <ScrollArea className="flex-1 px-6">
        <div className="space-y-6 py-6">
          {sortedMessages.map((message) => (
            <ChatMessageBubble key={message.id} message={message} />
          ))}
          {isStreaming && <ChatMessageSkeleton />}
        </div>
      </ScrollArea>
      <div className="border-t border-border/80 px-6 py-4">
        <ChatInput />
      </div>
    </Card>
  );
}
