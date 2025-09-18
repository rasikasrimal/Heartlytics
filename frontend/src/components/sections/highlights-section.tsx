import { BarChart3, CircuitBoard, Share2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { PageSection } from "../layout/page-section";

const highlights = [
  {
    icon: CircuitBoard,
    title: "Composable primitives",
    body: "Use Tailwind and shadcn-inspired components to compose surfaces that stay consistent across experiments."
  },
  {
    icon: Share2,
    title: "Tooling aware",
    body: "Stream responses, trigger tool calls, and show audit trails directly in your demo. Perfect for showcasing LLM agents."
  },
  {
    icon: BarChart3,
    title: "Analytics ready",
    body: "Bring cohort metrics, outcome trends, and telemetry digests into reusable cards, tabs, and timelines."
  }
];

export function HighlightsSection() {
  return (
    <PageSection tone="muted">
      <div className="grid gap-6 lg:grid-cols-3">
        {highlights.map((item) => (
          <Card key={item.title} className="h-full border-border/70 shadow-soft">
            <CardHeader className="space-y-3">
              <item.icon className="h-5 w-5 text-primary" />
              <CardTitle className="font-display text-xl text-secondary">
                {item.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              {item.body}
            </CardContent>
          </Card>
        ))}
      </div>
    </PageSection>
  );
}
