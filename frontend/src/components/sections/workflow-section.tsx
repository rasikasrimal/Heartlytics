import { ArrowRight, Beaker, ShieldCheck, Stethoscope } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { PageSection } from "../layout/page-section";

const steps = [
  {
    title: "Frame the clinical question",
    description: "Align product, clinical, and data teams using reusable storyboards and guided prompts.",
    icon: Stethoscope
  },
  {
    title: "Model and evaluate",
    description: "Wire up inference endpoints, orchestrate tool calls, and run evaluation cells in the same surface.",
    icon: Beaker
  },
  {
    title: "Ship with confidence",
    description: "Present the outcomes with governance snapshots, audit logs, and patient safety guardrails baked in.",
    icon: ShieldCheck
  }
];

export function WorkflowSection() {
  return (
    <PageSection id="workflow" tone="muted">
      <div className="space-y-10">
        <div className="max-w-2xl space-y-3">
          <h2 className="font-display text-3xl text-secondary">From idea to deployed pilot.</h2>
          <p className="text-base text-muted-foreground">
            The studio keeps teams aligned from first concept to clinical rollout. Each
            step can be demoed, reviewed, and iterated live with stakeholders.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {steps.map((step, index) => (
            <Card key={step.title} className="relative border-border/60 shadow-soft">
              <CardHeader className="space-y-2">
                <step.icon className="h-5 w-5 text-primary" />
                <CardTitle className="font-display text-xl text-secondary">
                  {index + 1}. {step.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-muted-foreground">
                <p>{step.description}</p>
                {index < steps.length - 1 ? (
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </PageSection>
  );
}
