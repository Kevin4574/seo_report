// frontend/app/layout.tsx
import "@/styles/globals.css";
import type { ReactNode } from "react";
import Starfield from "@/components/Starfield";

export const metadata = {
  title: "SEO Audit",
  description: "One-click SEO scoring tool",
  openGraph: {
    title: "SEO Audit",
    description: "Gorgeous, AI-enhanced SEO reports in seconds",
    images: [
      {
        url: "/og-default.png", // 你也可以换成后端生成的封面图地址
        width: 1200,
        height: 630,
      },
    ],
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="relative flex flex-col min-h-[100dvh] overflow-x-hidden">
        {/* 全局星空背景 */}
        <Starfield />

        {children}
      </body>
    </html>
  );
}
