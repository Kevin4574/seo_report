// frontend/components/ProgressBar.tsx
"use client";

export default function ProgressBar({
  value,
  label
}: {
  value: number;
  label: string;
}) {
  return (
    <div className="w-full max-w-xl flex flex-col gap-2">
      <span className="text-sm text-center">{label}</span>
      <div className="w-full h-3 bg-gray-700/40 rounded overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-teal-400 to-indigo-500"
          style={{ width: `${value}%`, transition: "width .3s" }}
        />
      </div>
    </div>
  );
}
