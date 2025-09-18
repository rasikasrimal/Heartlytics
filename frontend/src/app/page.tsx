import { AppShell } from "@/components/layout/app-shell";
import { ChatPanel } from "@/components/chat/chat-panel";
import { HeroHeader } from "@/components/layout/hero-header";
import { QuickActions } from "@/components/layout/quick-actions";

export default function HomePage() {
  return (
    <AppShell>
      <div className="space-y-12">
        <HeroHeader />
        <QuickActions />
        <section className="grid gap-8 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <ChatPanel />
          </div>
          <aside className="space-y-6 lg:col-span-2">
            <div className="rounded-2xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur">
              <h2 className="font-display text-lg font-semibold text-secondary-foreground">
                Experiment Faster</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Prototype multi-turn conversations, stream responses, and showcase tool
                integrations in a polished playground designed for rapid iteration.
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur">
              <h2 className="font-display text-lg font-semibold text-secondary-foreground">
                Build With Confidence
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Use the modular component system to compose demos, capture insights, and
                share learnings across the Heartlytics team.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </AppShell>
  );
}
