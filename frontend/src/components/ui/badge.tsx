import * as React from "react";

import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "outline" | "accent";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-wide",
        variant === "default" && "border-transparent bg-secondary text-secondary-foreground",
        variant === "outline" && "border-border bg-transparent text-muted-foreground",
        variant === "accent" && "border-transparent bg-accent/20 text-accent",
        className
      )}
      {...props}
    />
  );
}
