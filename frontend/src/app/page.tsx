import { AppShell } from "@/components/layout/app-shell";
import { CtaSection } from "@/components/sections/cta-section";
import { HeroSection } from "@/components/sections/hero-section";
import { HighlightsSection } from "@/components/sections/highlights-section";
import { InsightsSection } from "@/components/sections/insights-section";
import { WorkbenchSection } from "@/components/sections/workbench-section";
import { WorkflowSection } from "@/components/sections/workflow-section";

export default function HomePage() {
  return (
    <AppShell>
      <HeroSection />
      <HighlightsSection />
      <WorkbenchSection />
      <InsightsSection />
      <WorkflowSection />
      <CtaSection />
    </AppShell>
  );
}
