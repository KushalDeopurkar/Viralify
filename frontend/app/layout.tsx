import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Viralify — Predict if your content will go viral",
  description:
    "AI-powered content analysis that predicts viral potential using NLP and the STEPPS framework",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
