import { PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

interface PageSectionProps extends PropsWithChildren {
  id?: string;
  className?: string;
  tone?: "default" | "muted";
}

export function PageSection({ id, tone = "default", className, children }: PageSectionProps) {
  return (
    <section
      id={id}
      className={cn(
        "relative py-16",
        tone === "muted" && "bg-muted/40",
        className
      )}
    >
      <div className="mx-auto max-w-6xl px-6">{children}</div>
    </section>
  );
}
