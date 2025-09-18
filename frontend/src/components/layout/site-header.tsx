import Link from "next/link";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "#product", label: "Product" },
  { href: "#workbench", label: "Workbench" },
  { href: "#insights", label: "Insights" },
  { href: "#workflow", label: "Workflow" }
];

export function SiteHeader() {
  return (
    <header className="relative z-10 border-b border-border/80 bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="font-display text-lg font-semibold tracking-tight">
          Heartlytics Studio
        </Link>
        <nav className="hidden items-center gap-8 text-sm font-medium text-muted-foreground lg:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "transition-colors hover:text-foreground",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/docs">Docs</Link>
          </Button>
          <Button variant="primary" size="sm">
            Launch demo
          </Button>
        </div>
      </div>
    </header>
  );
}
