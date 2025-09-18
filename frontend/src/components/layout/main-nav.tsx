import Link from "next/link";
import { BrainCircuit, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

export function MainNav() {
  return (
    <header className="flex items-center justify-between rounded-2xl border border-border/60 bg-card/40 px-6 py-4 shadow-sm backdrop-blur">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-secondary-foreground">
          <BrainCircuit className="h-5 w-5" />
        </span>
        <div className="space-y-1">
          <Link href="/" className="font-display text-lg font-semibold tracking-tight">
            Heartlytics Studio
          </Link>
          <p className="text-xs text-muted-foreground">Prototype experiences with medical AI safely.</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" className="text-xs">
          Docs
        </Button>
        <Button variant="primary" size="sm" className="text-xs">
          <Sparkles className="mr-2 h-4 w-4" />
          Launch Demo
        </Button>
      </div>
    </header>
  );
}
