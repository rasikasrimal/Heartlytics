"use client";

import { FormEvent, useState } from "react";

import { Loader2, Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatComposerProps {
  onSubmit: (value: string) => Promise<void> | void;
  disabled?: boolean;
}

export function ChatComposer({ onSubmit, disabled }: ChatComposerProps) {
  const [value, setValue] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!value.trim() || disabled) return;

    await onSubmit(value);
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Ask the Heartlytics assistant to explore a new scenario..."
        className="min-h-[96px] resize-none"
        disabled={disabled}
      />
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Streaming is simulated for demo purposes—perfect for showcasing agent flows.
        </p>
        <Button type="submit" size="sm" disabled={disabled || !value.trim()}>
          {disabled ? (
            <>
              <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
              Streaming
            </>
          ) : (
            <>
              Send
              <Send className="ml-2 h-3.5 w-3.5" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
