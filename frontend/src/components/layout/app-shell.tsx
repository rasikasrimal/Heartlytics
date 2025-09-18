import { ReactNode } from "react";

import { MainNav } from "@/components/layout/main-nav";
import { MotionBackground } from "@/components/layout/motion-background";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-background via-background to-muted">
      <MotionBackground />
      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 pb-20 pt-10 sm:px-8 lg:px-12">
        <MainNav />
        <main className="mt-12 flex-1 pb-16">{children}</main>
      </div>
    </div>
  );
}
