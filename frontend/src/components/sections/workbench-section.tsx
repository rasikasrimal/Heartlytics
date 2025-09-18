import { Activity, Zap } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { PageSection } from "../layout/page-section";
import { ChatPreview } from "../chat/chat-preview";

export function WorkbenchSection() {
  return (
    <PageSection id="workbench" className="pt-10">
      <div className="grid gap-10 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
        <ChatPreview />
        <div className="space-y-6">
          <Card className="border-border/70 shadow-soft">
            <CardHeader className="space-y-3">
              <CardTitle className="font-display text-xl text-secondary">
                Why it works for demos
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p>
                The workbench mirrors the Heartlytics agent runtime: streaming turns,
                multi-step tool orchestration, and quick scenario triggers. It helps your
                team narrate complex workflows in a polished, repeatable way.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <Activity className="mt-1 h-4 w-4 text-primary" />
                  <span>Simulate clinician journeys with multi-turn guidance.</span>
                </li>
                <li className="flex items-start gap-3">
                  <Zap className="mt-1 h-4 w-4 text-accent" />
                  <span>Trigger tool calls and show structured results without backend wiring.</span>
                </li>
              </ul>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-muted/40 shadow-soft">
            <CardHeader>
              <CardTitle className="font-display text-lg text-secondary">
                Plug in your data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                Swap the static responses with your API hooks or streaming endpoints.
                Every UI primitive is modular—drop in new cohorts, metrics, or evaluation
                widgets without rebuilding layouts.
              </p>
              <p>
                The Zustand store exposes a consistent contract so you can hook in live
                inference without changing the surface area.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageSection>
  );
}
