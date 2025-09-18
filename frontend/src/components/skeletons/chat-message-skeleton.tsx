import { cn } from "@/lib/utils";

export function ChatMessageSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("flex gap-3", className)}>
      <div className="mt-1 h-8 w-8 flex-shrink-0 rounded-full bg-muted animate-pulse" />
      <div className="flex-1 space-y-3">
        <div className="h-3 w-24 rounded-full bg-muted animate-pulse" />
        <div className="h-3 w-full rounded-full bg-muted animate-pulse" />
        <div className="h-3 w-3/5 rounded-full bg-muted animate-pulse" />
      </div>
    </div>
  );
}
