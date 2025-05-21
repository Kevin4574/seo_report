// frontend/components/SearchBox.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import LoadingOverlay from "./LoadingOverlay";

export default function SearchBox() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error("Network response was not ok");
      const { id } = await res.json();
      router.push(`/report/${id}`);
    } catch (err) {
      console.error(err);
      setLoading(false);
      // 这里可以加一个 toast 通知
    }
  }

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-xl flex flex-col gap-4"
      >
        <input
          type="url"
          required
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="glass w-full px-5 py-4 rounded-lg text-lg placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-teal-400/50"
        />

        <button
          type="submit"
          disabled={loading}
          className="glass px-6 py-3 rounded-lg text-lg font-medium bg-gradient-to-r from-teal-400 to-indigo-500 hover:scale-[1.03] transition-transform disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Start Audit"}
        </button>
      </form>
      <LoadingOverlay show={loading} />
    </>
  );
}
