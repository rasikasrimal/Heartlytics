import { ArrowUpRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

import { PageSection } from "../layout/page-section";

export function CtaSection() {
  return (
    <PageSection id="cta" className="pb-20">
      <Card className="border-border/70 bg-secondary text-secondary-foreground shadow-float">
        <CardContent className="flex flex-col gap-6 rounded-3xl px-8 py-10 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-3">
            <h3 className="font-display text-3xl">Bring Heartlytics to your next review.</h3>
            <p className="max-w-xl text-sm text-secondary-foreground/80">
              Spin up polished demos, document your experiments, and keep clinicians in
              the loop. The studio is ready for your data and your workflows.
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            <Button variant="outline" size="lg" className="border-white/40 text-secondary-foreground">
              Schedule a walkthrough
            </Button>
            <Button variant="primary" size="lg" className="bg-accent text-accent-foreground hover:bg-accent/90" asChild>
              <a href="mailto:studio@heartlytics.ai" className="inline-flex items-center gap-2">
                Talk with our team
                <ArrowUpRight className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </PageSection>
  );
}
