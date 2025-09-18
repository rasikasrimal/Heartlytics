import type { Metadata } from "next";

import { inter, manrope, plexSans } from "@/styles/fonts";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Heartlytics Studio",
  description:
    "Next-gen Heartlytics front-end workbench with streaming chat, tooling hooks, and reusable UI primitives."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${manrope.variable} ${plexSans.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
