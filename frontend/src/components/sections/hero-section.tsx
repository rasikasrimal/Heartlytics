import { ArrowUpRight, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { formatNumber } from "@/lib/utils";

import { PageSection } from "../layout/page-section";

const stats = [
  { label: "Signals harmonized", value: 128_000 },
  { label: "Clinical workflows", value: 42 },
  { label: "Avg. build time saved", value: "63%" }
];

export function HeroSection() {
  return (
    <PageSection id="product" className="pt-28">
      <div className="grid items-center gap-12 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-8">
          <Badge variant="accent" className="w-fit">
            <Sparkles className="mr-2 h-3.5 w-3.5" /> Cardiovascular AI workbench
          </Badge>
          <div className="space-y-4">
            <h1 className="font-display text-4xl tracking-tight text-secondary">
              Build and demo Heartlytics experiences with confidence.
            </h1>
            <p className="max-w-xl text-base text-muted-foreground">
              Heartlytics Studio gives your team a reusable design system, live-streaming
              chat playground, and instrumentation to craft convincing prototypes in
              minutes—not weeks.
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            <Button variant="primary" size="lg">
              Start prototyping
            </Button>
            <Button variant="outline" size="lg" asChild>
              <a href="#workbench" className="inline-flex items-center gap-2">
                Explore the workbench
                <ArrowUpRight className="h-4 w-4" />
              </a>
            </Button>
          </div>
          <dl className="grid gap-6 sm:grid-cols-3">
            {stats.map((stat) => (
              <div key={stat.label}>
                <dt className="text-xs uppercase tracking-wide text-muted-foreground">
                  {stat.label}
                </dt>
                <dd className="mt-2 font-display text-2xl text-secondary">
                  {typeof stat.value === "number" ? formatNumber(stat.value) : stat.value}
                </dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="space-y-4">
          <Card className="border-border/80 shadow-soft">
            <CardContent className="space-y-4 p-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-secondary">Demo ready templates</p>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
              </div>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="rounded-xl border border-dashed border-border/70 p-3">
                  Streaming chat & tool orchestration harness
                </li>
                <li className="rounded-xl border border-dashed border-border/70 p-3">
                  Cohort analytics dashboards with dynamic filters
                </li>
                <li className="rounded-xl border border-dashed border-border/70 p-3">
                  Clinician-facing briefing layouts and data stories
                </li>
              </ul>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-primary/5 shadow-soft">
            <CardContent className="space-y-3 p-5">
              <p className="text-sm font-semibold text-secondary">Prototype focus</p>
              <p className="text-sm text-secondary/70">
                Deploy consistent typography, spacing, and color tokens with every
                experiment. Reuse blocks, swap data sources, and stay visually on brand.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageSection>
  );
}
