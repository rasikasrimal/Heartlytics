export type Author = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  author: Author;
  content: string;
  createdAt: number;
  streaming?: boolean;
}

export interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  sendMessage: (input: string) => Promise<void>;
  appendAssistantMessage: (chunk: string) => void;
  completeStreaming: () => void;
}
