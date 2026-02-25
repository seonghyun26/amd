import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MDA — MD Simulation Agent",
  description: "Claude-powered molecular dynamics simulation assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="h-screen overflow-hidden bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
        {children}
      </body>
    </html>
  );
}
