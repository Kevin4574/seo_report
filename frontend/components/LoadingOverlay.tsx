// frontend/components/LoadingOverlay.tsx
"use client";

import { motion, AnimatePresence } from "framer-motion";

export interface Progress {
  value: number;
  label: string;
}

export default function LoadingOverlay({
  show,
  progress,
}: {
  show: boolean;
  progress?: Progress;
}) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="fixed inset-0 z-50 flex flex-col items-center
                     justify-center gap-6 bg-black/70 backdrop-blur-md"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {progress && (
            <div className="w-64 text-center">
              <span className="block mb-2 text-sm">{progress.label}</span>
              <div className="h-2 w-full bg-gray-700/40 rounded overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-teal-400 to-indigo-500"
                  style={{ width: `${progress.value}%`, transition: "width .3s" }}
                />
              </div>
            </div>
          )}

          {/* 旋转圈 */}
          <motion.span
            className="h-14 w-14 border-4 border-t-transparent
                       border-teal-400 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
