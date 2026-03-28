import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Finance Copilot",
  description: "Corporate Finance Autopilot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
