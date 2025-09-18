export type Author = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  author: Author;
  content: string;
  createdAt: number;
  streaming?: boolean;
}

export interface ChatSuggestion {
  id: string;
  title: string;
  description: string;
  prompt: string;
}

export type ToolRunStatus = "queued" | "running" | "succeeded";

export interface ToolRun {
  id: string;
  name: string;
  triggeredBy: string;
  arguments: string;
  summary: string;
  result: string;
  status: ToolRunStatus;
  startedAt: number;
  finishedAt?: number;
}

export interface ChatScenario {
  id: string;
  responseChunks: string[];
  toolRun?: Omit<ToolRun, "id" | "status" | "startedAt" | "finishedAt">;
}

export interface ChatState {
  messages: ChatMessage[];
  toolRuns: ToolRun[];
  suggestions: ChatSuggestion[];
  isStreaming: boolean;
  sendMessage: (input: string, options?: { scenarioId?: string }) => Promise<void>;
  runSuggestion: (id: string) => Promise<void>;
  resetConversation: () => void;
}
