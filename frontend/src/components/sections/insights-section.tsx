import { BrainCircuit, ClipboardList, Sparkle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { PageSection } from "../layout/page-section";

const insights = [
  {
    title: "Telemetry digests",
    body: "Summaries built for cardiology rounds and operational stand-ups, backed by streaming signal monitoring.",
    icon: BrainCircuit
  },
  {
    title: "Governance ready",
    body: "Document assumption tracking, audit runs, and evaluation verdicts without leaving the prototype.",
    icon: ClipboardList
  },
  {
    title: "Narrative first",
    body: "Pair quantitative insights with story-driven layouts, ensuring stakeholders grasp the impact instantly.",
    icon: Sparkle
  }
];

export function InsightsSection() {
  return (
    <PageSection id="insights">
      <div className="space-y-12">
        <div className="max-w-2xl space-y-3">
          <Badge variant="outline" className="w-fit">
            Insightful by default
          </Badge>
          <h2 className="font-display text-3xl text-secondary">Data storytelling, done for you.</h2>
          <p className="text-base text-muted-foreground">
            Rapidly compose dashboards, progress trackers, and clinician-ready briefs.
            The same building blocks power streaming chat transcripts and structured
            analytics panels.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {insights.map((insight) => (
            <Card key={insight.title} className="border-border/70 shadow-soft">
              <CardHeader className="space-y-3">
                <insight.icon className="h-5 w-5 text-accent" />
                <CardTitle className="font-display text-xl text-secondary">
                  {insight.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                {insight.body}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </PageSection>
  );
}
