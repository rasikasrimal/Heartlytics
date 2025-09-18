import { Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function HeroHeader() {
  return (
    <section className="space-y-5">
      <Badge variant="accent" className="w-fit">
        New • Streaming-ready playground
      </Badge>
      <div className="space-y-4">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-secondary-foreground sm:text-4xl">
          Prototype Heartlytics conversations in minutes
        </h1>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
          Assemble multi-modal experiences with reusable components, consistent typography,
          and built-in streaming states. Designed for clarity, iteration speed, and a
          polished, demo-ready finish.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/40 px-3 py-2">
          <Sparkles className="h-4 w-4 text-accent" />
          <span>Streaming simulation</span>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/40 px-3 py-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          Tool integrations ready
        </span>
        <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/40 px-3 py-2">
          <span className="h-2 w-2 rounded-full bg-accent" />
          Modular UI tokens
        </span>
      </div>
    </section>
  );
}
