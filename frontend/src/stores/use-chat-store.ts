"use client";

import { nanoid } from "nanoid";
import { create } from "zustand";
import { devtools } from "zustand/middleware";

import { STREAMING_INTERVAL } from "@/lib/utils";
import type { ChatMessage, ChatState } from "@/types/chat";

const assistantSeed = `Hi there! I'm the Heartlytics studio assistant. I can help you
prototype streaming conversations, configure tool calls, and showcase data-rich
insights. Ask me anything or try one of the quick actions to see what's possible.`;

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      messages: [
        {
          id: nanoid(),
          author: "assistant",
          content: assistantSeed,
          createdAt: Date.now()
        }
      ],
      isStreaming: false,
      async sendMessage(input) {
        if (!input.trim()) {
          return;
        }

        const userMessage: ChatMessage = {
          id: nanoid(),
          author: "user",
          content: input,
          createdAt: Date.now()
        };

        set((state) => ({
          messages: [...state.messages, userMessage, createStreamingMessage()],
          isStreaming: true
        }));

        const chunks = buildAssistantResponse(input);

        for (const chunk of chunks) {
          await new Promise((resolve) => setTimeout(resolve, STREAMING_INTERVAL));
          get().appendAssistantMessage(chunk);
        }

        get().completeStreaming();
      },
      appendAssistantMessage(chunk) {
        set((state) => ({
          messages: state.messages.map((message) =>
            message.streaming
              ? {
                  ...message,
                  content: `${message.content}${chunk}`
                }
              : message
          )
        }));
      },
      completeStreaming() {
        set((state) => ({
          messages: state.messages.map((message) =>
            message.streaming
              ? {
                  ...message,
                  streaming: false
                }
              : message
          ),
          isStreaming: false
        }));
      }
    }),
    { name: "chat-store" }
  )
);

function createStreamingMessage(): ChatMessage {
  return {
    id: nanoid(),
    author: "assistant",
    content: "",
    createdAt: Date.now(),
    streaming: true
  };
}

function buildAssistantResponse(input: string) {
  const thoughts = [
    "Let me think...",
    "Here's a suggestion to keep your prototype consistent:",
    "We can route this through an evaluation cell for realtime analytics.",
    "Would you like to add a synthetic patient cohort to compare outcomes?"
  ];

  const base = `Thanks for sharing: "${input}". Let's craft a structured plan to test it.`;

  return [base, "\n\n", thoughts[Math.floor(Math.random() * thoughts.length)]];
}
