"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useChatStore } from "@/stores/use-chat-store";

export function ChatInput() {
  const [value, setValue] = useState("");
  const sendMessage = useChatStore((state) => state.sendMessage);
  const isStreaming = useChatStore((state) => state.isStreaming);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim() || isStreaming) {
      return;
    }

    await sendMessage(value.trim());
    setValue("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Textarea
        value={value}
        minLength={2}
        maxLength={2000}
        placeholder="Ask the Heartlytics assistant..."
        onChange={(event) => setValue(event.target.value)}
        className="resize-none"
      />
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Shift + Enter to add a newline</span>
        <Button type="submit" size="sm" variant="primary" disabled={isStreaming || value.trim().length === 0}>
          <Send className="mr-2 h-4 w-4" />
          Send
        </Button>
      </div>
    </form>
  );
}
