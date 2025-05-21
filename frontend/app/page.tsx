// frontend/app/page.tsx
"use client";

import { motion } from "framer-motion";
import { Pyramid } from "lucide-react";
import SearchBox from "@/components/SearchBox";

export default function HomePage() {
  return (
    <main className="flex flex-col items-center justify-center flex-1 gap-y-12 px-6 py-16">
      {/* Logo + 标题 with 动感光环 */}
      <motion.div
        className="logo-wrapper"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <Pyramid size={60} strokeWidth={2} className="text-teal-400" />
        <h1 className="text-6xl sm:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-indigo-500">
          SEO Audit
        </h1>
      </motion.div>

      {/* 副标题淡入 */}
      <motion.p
        className="text-2xl max-w-2xl text-center leading-relaxed"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        Paste a URL and get a gorgeous, AI-enhanced SEO report&nbsp;in&nbsp;seconds —
        scores, charts and actionable insights, all in one place.
      </motion.p>

      {/* 搜索框 */}
      <SearchBox />
    </main>
  );
}
