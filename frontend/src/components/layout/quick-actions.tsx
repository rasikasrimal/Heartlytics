"use client";

import { Lightbulb, Rocket, Stethoscope } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { useChatStore } from "@/stores/use-chat-store";

const actions = [
  {
    title: "Stream care plan summary",
    description: "Simulate a structured assistant response summarizing clinical updates.",
    icon: Stethoscope,
    prompt: "Summarize the latest patient vitals and recommend adjustments to the care plan."
  },
  {
    title: "Prototype tool call",
    description: "Showcase how Heartlytics tools can surface real-time analytics.",
    icon: Rocket,
    prompt: "Run an analytics tool to compare recovery rates across two cohorts."
  },
  {
    title: "Brainstorm next steps",
    description: "Use the assistant to ideate on future product experiments.",
    icon: Lightbulb,
    prompt: "Propose three experiments to validate clinical decision support accuracy."
  }
];

export function QuickActions() {
  const sendMessage = useChatStore((state) => state.sendMessage);

  return (
    <section className="grid gap-4 md:grid-cols-3">
      {actions.map((action) => (
        <Card key={action.title} className="flex h-full flex-col gap-4">
          <div className="flex items-center gap-3 text-secondary-foreground">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary/80 text-secondary-foreground">
              <action.icon className="h-4 w-4" />
            </span>
            <div>
              <CardTitle>{action.title}</CardTitle>
              <CardDescription>{action.description}</CardDescription>
            </div>
          </div>
          <Button
            variant="ghost"
            className="mt-auto w-fit text-xs text-muted-foreground hover:text-secondary-foreground"
            onClick={() => sendMessage(action.prompt)}
          >
            Use prompt
          </Button>
        </Card>
      ))}
    </section>
  );
}
