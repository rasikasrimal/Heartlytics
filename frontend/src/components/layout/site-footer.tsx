import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="relative z-10 border-t border-border/60 bg-background/90">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="font-display text-base font-semibold">Heartlytics Studio</p>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">
            Prototype, validate, and ship cardiovascular AI experiences with a cohesive
            design system and tool-ready playground.
          </p>
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <Link href="/privacy" className="hover:text-foreground">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-foreground">
            Terms
          </Link>
          <Link href="mailto:studio@heartlytics.ai" className="hover:text-foreground">
            Contact
          </Link>
        </div>
      </div>
    </footer>
  );
}
