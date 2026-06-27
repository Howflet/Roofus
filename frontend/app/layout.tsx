import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Roofus — Atlanta's Smartest Rooftops for Urban Agriculture",
  description:
    "Discover and score rooftops for urban agriculture potential in Hapeville, GA. Data-driven viability analysis for multifamily buildings.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
