"use client";

import { motion } from "framer-motion";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatStore } from "@/stores/use-chat-store";

import { ChatComposer } from "./chat-composer";
import { ChatMessageBubble } from "./chat-message";
import { ChatSuggestions } from "./chat-suggestions";
import { ToolRunCard } from "./tool-run-card";

export function ChatPreview() {
  const { messages, suggestions, toolRuns, isStreaming, sendMessage, runSuggestion, resetConversation } =
    useChatStore((state) => ({
      messages: state.messages,
      suggestions: state.suggestions,
      toolRuns: state.toolRuns,
      isStreaming: state.isStreaming,
      sendMessage: state.sendMessage,
      runSuggestion: state.runSuggestion,
      resetConversation: state.resetConversation
    }));

  return (
    <div className="space-y-6">
      <Card className="border-border/70 shadow-soft">
        <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="font-display text-xl text-secondary">
              Assistant workbench
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Streamed responses, quick scenarios, and tool executions ready for demos.
            </p>
          </div>
          <button
            type="button"
            className="text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-secondary"
            onClick={resetConversation}
          >
            Reset conversation
          </button>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="rounded-2xl border border-border/70 bg-background/80 p-4">
            <ScrollArea className="h-72 pr-3">
              <div className="space-y-5">
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChatMessageBubble message={message} />
                  </motion.div>
                ))}
              </div>
            </ScrollArea>
          </div>
          <ChatSuggestions
            suggestions={suggestions}
            onSelect={runSuggestion}
            disabled={isStreaming}
          />
          <ChatComposer onSubmit={sendMessage} disabled={isStreaming} />
        </CardContent>
      </Card>
      {toolRuns.length > 0 ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {toolRuns.map((toolRun) => (
            <motion.div
              key={toolRun.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.24 }}
            >
              <ToolRunCard toolRun={toolRun} />
            </motion.div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
