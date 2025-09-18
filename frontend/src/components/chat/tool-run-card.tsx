import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDuration, formatRelativeTime } from "@/lib/utils";
import type { ToolRun } from "@/types/chat";

interface ToolRunCardProps {
  toolRun: ToolRun;
}

export function ToolRunCard({ toolRun }: ToolRunCardProps) {
  const duration =
    toolRun.finishedAt && toolRun.startedAt
      ? formatDuration(toolRun.finishedAt - toolRun.startedAt)
      : undefined;

  return (
    <Card className="border-border/70 shadow-soft">
      <CardHeader className="space-y-2">
        <div className="flex items-center justify-between">
          <CardTitle className="font-display text-base text-secondary">
            {toolRun.name}
          </CardTitle>
          <Badge variant="accent">{toolRun.status}</Badge>
        </div>
        <p className="text-xs uppercase tracking-wide text-muted-foreground">
          Triggered by {toolRun.triggeredBy} · {formatRelativeTime(toolRun.startedAt)}
        </p>
      </CardHeader>
      <CardContent className="space-y-4 text-sm text-muted-foreground">
        <p>{toolRun.summary}</p>
        <div className="rounded-xl border border-dashed border-border/70 bg-background/80 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Arguments
          </p>
          <p className="mt-1 text-xs font-mono text-secondary/80">
            {toolRun.arguments}
          </p>
        </div>
        <div className="rounded-xl border border-dashed border-border/70 bg-muted/50 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Result
          </p>
          <p className="mt-1 text-sm text-secondary/80">{toolRun.result}</p>
        </div>
        {duration ? (
          <p className="text-xs text-muted-foreground">Execution time: {duration}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}
