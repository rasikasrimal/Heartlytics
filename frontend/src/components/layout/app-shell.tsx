import { PropsWithChildren } from "react";

import { SiteFooter } from "./site-footer";
import { SiteHeader } from "./site-header";

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="relative flex min-h-screen flex-col bg-background">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 left-1/2 h-[38rem] w-[38rem] -translate-x-1/2 rounded-full bg-spotlight" />
        <div className="absolute inset-x-0 top-0 h-[1200px] bg-grid-slate bg-[length:40px_40px] opacity-[0.18]" />
      </div>
      <SiteHeader />
      <main className="relative flex-1 pb-24">{children}</main>
      <SiteFooter />
    </div>
  );
}
