"use client";

import { nanoid } from "nanoid";
import { create } from "zustand";
import { devtools } from "zustand/middleware";

import { STREAMING_INTERVAL, delay } from "@/lib/utils";
import type {
  ChatMessage,
  ChatState,
  ChatSuggestion,
  ChatScenario,
  ToolRun
} from "@/types/chat";

const suggestions: ChatSuggestion[] = [
  {
    id: "cohort",
    title: "Cohort builder",
    description: "Synthesize a stratified population for experimentation.",
    prompt:
      "Generate a cohort of 250 heart failure patients grouped by therapy adoption and social determinants. Summarize the highest risk segment."
  },
  {
    id: "readmission",
    title: "Readmission forecast",
    description: "Project 90-day readmission for the telemetry feed.",
    prompt:
      "Forecast the 90-day readmission probability for the streaming telemetry feed, and outline three modifiable risk factors we can intervene on."
  },
  {
    id: "triage",
    title: "Virtual triage",
    description: "Draft a remote triage plan using wearable signals.",
    prompt:
      "Design a triage workflow for a patient presenting chest tightness. Blend wearable ECG, voice biomarkers, and home labs to prioritize next actions."
  }
];

const suggestionDictionary = Object.fromEntries(
  suggestions.map((item) => [item.id, item])
);

const assistantIntro = `Welcome to the Heartlytics studio workbench. I can stream responses, orchestrate tool calls, and help you design rich cardiovascular experiments.`;

const scenarios: Record<string, ChatScenario> = {
  cohort: {
    id: "cohort",
    responseChunks: [
      "Great call. I'll compose a balanced cohort with synthetic telemetry. ",
      "\n\nKey segments emerging:\n",
      "• Precision therapy adopters show a 18% lower readmission rate.\n",
      "• Social vulnerability index above 0.6 correlates with a 2.4x alert rate.\n",
      "• Remote cardiac rehab enrollment reduces length of stay by 1.7 days.\n",
      "\n\nI'll surface the highest-risk cluster for you next."
    ],
    toolRun: {
      name: "cohort-synthesizer",
      triggeredBy: suggestionDictionary.cohort.title,
      arguments:
        '{"size":250,"filters":["NYHA II-IV","age > 55"],"features":["therapy_adoption","svi","remote_rehab"]}',
      summary: "Generated 3 synthetic clusters with telemetry features aligned to the latest Heartlytics registry.",
      result:
        "High-risk cluster: low rehab adherence, elevated SVI, and persistent tachycardia with a projected 34% readmission risk."
    }
  },
  readmission: {
    id: "readmission",
    responseChunks: [
      "Streaming vitals… pulling variability windows from the last 14 days. ",
      "\n\nRisk posture:\n",
      "• Baseline risk: 0.27 (±0.04) across the monitored cohort.\n",
      "• Today's telemetry spikes the index to 0.41 driven by nocturnal arrhythmias.\n",
      "• Recovery protocols lower projected risk to 0.19 if activated within 48 hours.\n",
      "\n\nLet's target the modifiable factors next."
    ],
    toolRun: {
      name: "readmission-forecast",
      triggeredBy: suggestionDictionary.readmission.title,
      arguments:
        '{"window":"14d","signals":["hrv","arrhythmia_events","activity"],"population":"remote_monitoring"}',
      summary: "Ran ensemble forecast against telemetry baselines and flag thresholds.",
      result:
        "Actionable levers: sleep regularity, loop diuretic adherence, and virtual coaching add-ons reduce projected readmissions by 22%."
    }
  },
  triage: {
    id: "triage",
    responseChunks: [
      "Reviewing voice biomarkers and wearable ECG feeds… ",
      "\n\nRecommended workflow:\n",
      "1. Trigger clinician review when the acoustic biomarker exceeds 0.65.\n",
      "2. Auto-order a high-sensitivity troponin when wearable ECG detects ST deviation >1mm.\n",
      "3. Escalate to telecardiology if remote BP trend stays above 150/95 for 3 hours.\n",
      "\nThis keeps in-person visits for the highest acuity cases."
    ],
    toolRun: {
      name: "triage-orchestrator",
      triggeredBy: suggestionDictionary.triage.title,
      arguments:
        '{"signals":["voice","wearable_ecg","home_bp"],"threshold_strategy":"dynamic"}',
      summary: "Drafted a remote triage ladder blending wearable data with clinician guardrails.",
      result:
        "Escalation ready. Triage playbook assembled with streaming guardrails and patient-facing nudges."
    }
  }
};

function baseMessages(): ChatMessage[] {
  return [
    {
      id: nanoid(),
      author: "assistant",
      content: assistantIntro,
      createdAt: Date.now()
    }
  ];
}

const initialState = () => ({
  messages: baseMessages(),
  toolRuns: [] as ToolRun[],
  suggestions,
  isStreaming: false
});

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      ...initialState(),
      async sendMessage(input, options) {
        const value = input.trim();
        if (!value) return;

        const scenario = resolveScenario(value, options?.scenarioId);
        const streamId = nanoid();
        const timestamp = Date.now();

        const userMessage: ChatMessage = {
          id: nanoid(),
          author: "user",
          content: value,
          createdAt: timestamp
        };

        set((state) => ({
          messages: [
            ...state.messages,
            userMessage,
            {
              id: streamId,
              author: "assistant",
              content: "",
              createdAt: Date.now(),
              streaming: true
            }
          ],
          isStreaming: true
        }));

        for (const chunk of scenario.responseChunks) {
          await delay(STREAMING_INTERVAL);
          set((state) => ({
            messages: state.messages.map((message) =>
              message.id === streamId
                ? { ...message, content: `${message.content}${chunk}` }
                : message
            )
          }));
        }

        const completedAt = Date.now();

        set((state) => ({
          messages: state.messages.map((message) =>
            message.id === streamId ? { ...message, streaming: false } : message
          ),
          isStreaming: false,
          toolRuns: scenario.toolRun
            ? [
                {
                  id: nanoid(),
                  status: "succeeded",
                  startedAt: timestamp,
                  finishedAt: completedAt,
                  ...scenario.toolRun
                },
                ...state.toolRuns
              ].slice(0, 3)
            : state.toolRuns
        }));
      },
      async runSuggestion(id) {
        const suggestion = get().suggestions.find((item) => item.id === id);
        if (!suggestion) return;

        await get().sendMessage(suggestion.prompt, { scenarioId: id });
      },
      resetConversation() {
        set(initialState());
      }
    }),
    { name: "chat-preview" }
  )

);

function resolveScenario(input: string, scenarioId?: string): ChatScenario {
  if (scenarioId && scenarios[scenarioId]) {
    return scenarios[scenarioId];
  }

  const summary = input.length > 120 ? `${input.slice(0, 120)}…` : input;

  return {
    id: "adaptive",
    responseChunks: [
      "Thanks for the context. I'll evaluate the telemetry and craft a plan. ",
      "\n\nNext best steps:\n",
      "• Harmonize wearable, EHR, and claims signals in a staging sandbox.\n",
      "• Simulate counterfactual outcomes using recent cardiovascular twins.\n",
      "• Surface a clinician-ready brief with risk drift indicators.\n",
      "\nReady when you want to launch the run."
    ],
    toolRun: {
      name: "signal-harmonizer",
      triggeredBy: "Adaptive prompt",
      arguments: JSON.stringify({ query: summary }),
      summary: "Mapped cross-source telemetry to the unified Heartlytics schema.",
      result: "Insights queued. Generated a monitoring brief with anomaly windows and suggested guardrails."
    }
  };
}
