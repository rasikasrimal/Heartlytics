"use client";

import { ChatSuggestion } from "@/types/chat";

import { Button } from "../ui/button";

interface ChatSuggestionsProps {
  suggestions: ChatSuggestion[];
  onSelect: (id: string) => void;
  disabled?: boolean;
}

export function ChatSuggestions({ suggestions, onSelect, disabled }: ChatSuggestionsProps) {
  return (
    <div className="flex flex-wrap gap-3">
      {suggestions.map((suggestion) => (
        <Button
          key={suggestion.id}
          type="button"
          variant="ghost"
          size="sm"
          disabled={disabled}
          onClick={() => onSelect(suggestion.id)}
          className="h-auto items-start rounded-xl border border-dashed border-border/70 px-4 py-3 text-left text-sm"
        >
          <span className="font-medium text-secondary">{suggestion.title}</span>
          <span className="mt-1 block text-xs text-muted-foreground">
            {suggestion.description}
          </span>
        </Button>
      ))}
    </div>
  );
}
