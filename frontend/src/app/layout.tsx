import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GenAssess | Interview preparation",
  description: "Practice aptitude assessments and prepare for your next interview with GenAssess.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
